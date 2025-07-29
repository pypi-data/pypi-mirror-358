#![allow(clippy::literal_string_with_formatting_args)]

mod class_inject;
mod enums;
mod generator;
mod pyi;
mod structs;
mod unions;

use generator::Generator;
use std::{borrow::Cow, env::set_current_dir, fs, io, path::Path, process::Command};
use structs::StructBindGenerator;
use zip::ZipArchive;

const FLATC_DOWNLOAD_URL: &str = "https://github.com/google/flatbuffers/releases/download/v25.2.10/";

const SCHEMA_FOLDER: &str = "./flatbuffers-schema";
const SCHEMA_FOLDER_BACKUP: &str = "../flatbuffers-schema";
const RLBOT_FBS: &str = "schema/rlbot.fbs";
const FLATC_BINARY: &str = if cfg!(windows) {
    "binaries\\flatc.exe"
} else {
    "binaries/flatc"
};

const OUT_FOLDER: &str = "./src/generated";
pub const PYTHON_OUT_FOLDER: &str = "./src/python";

pub enum PythonBindType {
    Struct(structs::StructBindGenerator),
    Enum(enums::EnumBindGenerator),
    Union(unions::UnionBindGenerator),
}

impl PythonBindType {
    pub const BASE_TYPES: [&'static str; 6] = ["bool", "i32", "u32", "f32", "String", "u8"];
    pub const FROZEN_TYPES: [&'static str; 26] = [
        "ControllableInfo",
        "ControllableTeamInfo",
        "PredictionSlice",
        "BallPrediction",
        "GoalInfo",
        "BoostPad",
        "FieldInfo",
        "Physics",
        "GamePacket",
        "PlayerInfo",
        "ScoreInfo",
        "BallInfo",
        "Touch",
        "CollisionShape",
        "BoxShape",
        "SphereShape",
        "CylinderShape",
        "BoostPadState",
        "MatchInfo",
        "TeamInfo",
        "Vector2",
        "CoreMessage",
        "InterfaceMessage",
        "CorePacket",
        "InterfacePacket",
        "PlayerInput",
    ];
    pub const NO_SET_TYPES: [&'static str; 1] = ["PlayerClass"];
    pub const UNIONS: [&'static str; 6] = [
        "PlayerClass",
        "CollisionShape",
        "RelativeAnchor",
        "RenderType",
        "CoreMessage",
        "InterfaceMessage",
    ];

    pub const OPTIONAL_UNIONS: [&'static str; 1] = ["RelativeAnchor"];
    pub const DEFAULT_OVERRIDES: [(&'static str, &'static str, &'static str); 1] = [("Color", "a", "255")];
    pub const FIELD_ALIASES: [(&'static str, &'static str, &'static str); 1] = [("PlayerInfo", "player_id", "spawn_id")];
    pub const FREELIST_TYPES: [(&'static str, usize); 0] = [];

    fn new(path: &Path) -> Option<Self> {
        // get the filename without the extension
        let filename = path.file_stem().unwrap().to_str().unwrap();

        if filename == "mod" {
            return None;
        }

        // convert snake_case to CamelCase to get the struct name
        let mut struct_name = String::new();
        for c in filename.split('_') {
            struct_name.push_str(&c[..1].to_uppercase());
            struct_name.push_str(&c[1..]);
        }
        struct_name = struct_name
            .replace("Rlbot", "RLBot")
            .replace("Halign", "HAlign")
            .replace("Valign", "VAlign");

        let struct_t_name = format!("{struct_name}T");

        let contents = fs::read_to_string(path).ok()?;

        #[cfg(windows)]
        let contents = contents.replace("\r\n", "\n");

        let struct_def = format!("pub struct {struct_name}");
        let struct_def_pos = contents.find(&struct_def).unwrap();

        let mut docs = Vec::new();

        for line in contents[..struct_def_pos].lines().rev() {
            if line.starts_with("///") {
                docs.push(line.trim_start_matches("///").trim());
            } else {
                break;
            }
        }

        let struct_doc_str = if docs.is_empty() {
            None
        } else {
            Some(docs.into_iter().map(|s| s.to_string()).rev().collect::<Vec<_>>())
        };

        if let Some(types) = StructBindGenerator::get_types(&contents, &struct_t_name) {
            return Some(Self::Struct(StructBindGenerator::new(
                filename.to_string(),
                struct_name,
                struct_t_name,
                struct_doc_str,
                contents,
                types,
            )?));
        }

        if let Some((types, enum_type)) = enums::EnumBindGenerator::get_types(&contents, &struct_name) {
            return Some(match enum_type {
                enums::EnumType::Enum => {
                    Self::Enum(enums::EnumBindGenerator::new(filename.to_string(), struct_name, types)?)
                }
                enums::EnumType::Union => Self::Union(unions::UnionBindGenerator::new(
                    filename.to_string(),
                    struct_name,
                    struct_t_name,
                    types,
                )?),
            });
        }

        None
    }

    pub fn filename(&self) -> &str {
        match self {
            Self::Struct(bind) => bind.filename(),
            Self::Enum(bind) => bind.filename(),
            Self::Union(bind) => bind.filename(),
        }
    }

    pub fn struct_name(&self) -> &str {
        match self {
            Self::Struct(bind) => bind.struct_name(),
            Self::Enum(bind) => bind.struct_name(),
            Self::Union(bind) => bind.struct_name(),
        }
    }

    pub fn generate(&mut self, filepath: &Path) -> io::Result<()> {
        match self {
            Self::Struct(bind) => bind.generate(filepath),
            Self::Enum(bind) => bind.generate(filepath),
            Self::Union(bind) => bind.generate(filepath),
        }
    }
}

fn mod_rs_generator(type_data: &[PythonBindType]) -> io::Result<()> {
    let mut file_contents = Vec::new();

    for generator in type_data {
        let filename = generator.filename();

        file_contents.push(Cow::Owned(format!("mod {filename};")));
        file_contents.push(Cow::Owned(format!("pub use {filename}::*;")));
    }

    file_contents.push(Cow::Borrowed(""));

    fs::write(format!("{PYTHON_OUT_FOLDER}/mod.rs"), file_contents.join("\n"))?;

    Ok(())
}

fn run_flatc() {
    println!("cargo:rerun-if-changed=flatbuffers-schema/comms.fbs");
    println!("cargo:rerun-if-changed=flatbuffers-schema/gamedata.fbs");
    println!("cargo:rerun-if-changed=flatbuffers-schema/gamestatemanip.fbs");
    println!("cargo:rerun-if-changed=flatbuffers-schema/matchconfig.fbs");
    println!("cargo:rerun-if-changed=flatbuffers-schema/rendering.fbs");
    println!("cargo:rerun-if-changed=flatbuffers-schema/rlbot.fbs");

    set_current_dir(env!("CARGO_MANIFEST_DIR")).unwrap();

    let mut schema_folder = Path::new(SCHEMA_FOLDER);
    if !schema_folder.exists() {
        schema_folder = Path::new(SCHEMA_FOLDER_BACKUP);
        assert!(schema_folder.exists(), "Could not find flatbuffers schema folder");
    }

    let schema_folder_str = schema_folder.display();
    let flatc_str = format!("{schema_folder_str}/{FLATC_BINARY}");
    let flatc_path = Path::new(&flatc_str);

    if !flatc_path.exists() {
        fs::create_dir_all(flatc_path).unwrap();

        // if the flatc binary isn't found, download it
        let file_name = if cfg!(windows) {
            "Windows.flatc.binary.zip"
        } else {
            "Linux.flatc.binary.g++-13.zip"
        };
        let response = reqwest::blocking::get(format!("{FLATC_DOWNLOAD_URL}/{file_name}"))
            .map_err(|e| {
                eprintln!("Failed to download flatc binary: {e}");
                io::Error::other("Failed to download flatc binary")
            })
            .unwrap();
        let bytes = response
            .bytes()
            .map_err(|e| {
                eprintln!("Failed to read response stream when downloading flatc binary: {e}");
                io::Error::other("Failed to read response stream when downloading flatc binary")
            })
            .unwrap();

        // extract zip
        let mut zip = ZipArchive::new(io::Cursor::new(bytes)).unwrap();
        zip.extract(schema_folder).unwrap();

        assert!(flatc_path.exists(), "Failed to download flatc binary");
    }

    let mut proc = Command::new(flatc_str);

    proc.args([
        "--rust".as_ref(),
        "--gen-object-api".as_ref(),
        "--gen-all".as_ref(),
        "--filename-suffix".as_ref(),
        "".as_ref(),
        "--rust-module-root-file".as_ref(),
        "-o".as_ref(),
        OUT_FOLDER.as_ref(),
        schema_folder.join(RLBOT_FBS).as_os_str(),
    ])
    .spawn()
    .unwrap()
    .wait()
    .unwrap();

    assert!(proc.status().unwrap().success(), "flatc failed to run");
}

fn main() {
    run_flatc();

    let out_folder = Path::new(OUT_FOLDER).join("rlbot").join("flat");

    assert!(
        out_folder.exists(),
        "Could not find generated folder: {}",
        out_folder.display()
    );

    // read the current contents of the generated folder
    let generated_files = fs::read_dir(out_folder)
        .unwrap()
        .map(|res| res.map(|e| e.path()))
        .collect::<Result<Vec<_>, io::Error>>()
        .unwrap();

    let mut type_data = Vec::new();

    for path in generated_files {
        let Some(mut bind_generator) = PythonBindType::new(&path) else {
            continue;
        };

        bind_generator.generate(&path).unwrap();
        type_data.push(bind_generator);
    }

    mod_rs_generator(&type_data).unwrap();
    pyi::generator(&type_data).unwrap();
    class_inject::classes_to_lib_rs(&type_data).unwrap();
}

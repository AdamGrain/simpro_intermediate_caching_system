use std::env;
use std::fs;
use std::path::Path;
use progenitor::GenerationSettings;
use progenitor::InterfaceStyle;

fn main() {
    // OPENAPI_INPUT — path to the processed OpenAPI spec in YAML.
    let r#in: String = env::var("OPENAPI_INPUT").unwrap_or_else(|_| "openapi.yaml".to_string());
    let content: String = fs::read_to_string(&r#in).unwrap_or_else(|e| panic!("Cannot read '{}': {}", r#in, e));
    let parsed = serde_yaml::from_str(&content).unwrap_or_else(|e| panic!("Failed to parse '{}' as YAML: {}", r#in, e));
    let mut binding = GenerationSettings::default();
    let settings = binding.with_interface(InterfaceStyle::Builder);
    let mut generator = progenitor::Generator::new(&settings);
    let tokens = generator.generate_tokens(&parsed).unwrap();
    let ast = syn::parse2(tokens).unwrap_or_else(|e| panic!("Token parse failed: {}", e));
    let content = prettyplease::unparse(&ast);
    // CODEGEN_OUT — destination path for the generated api.rs.
    let out_path_str = env::var("CODEGEN_OUT").unwrap_or_else(|_| {
        let manifest_dir = env::var("CARGO_MANIFEST_DIR").unwrap();
        Path::new(&manifest_dir)
            .join("src")
            .join("api.rs")
            .to_string_lossy()
            .into_owned()
    });

    let output: &Path = Path::new(&out_path_str);
    if let Some(parent) = output.parent() {
        fs::create_dir_all(parent)
            .unwrap_or_else(|e| panic!("Cannot create directory '{}': {}", parent.display(), e));
    }
    fs::write(output, content)
        .unwrap_or_else(|e| panic!("Cannot write '{}': {}", output.display(), e));

    println!("cargo:info=Generated API client written to {}", output.display());
}

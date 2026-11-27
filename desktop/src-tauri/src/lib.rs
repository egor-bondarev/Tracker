//! Native side of the Tracker window: local files only. Queue logic and HTTP live in the UI.

use std::fs;
use std::path::{Path, PathBuf};

use tauri::Manager;

/// Files the UI may read and write in the app data directory.
const APP_FILES: [&str; 4] = [
    "settings.json",
    "tasks.json",
    "settings.broken.json",
    "tasks.broken.json",
];

fn app_file(app: &tauri::AppHandle, name: &str) -> Result<PathBuf, String> {
    if !APP_FILES.contains(&name) {
        return Err(format!("unknown file {name}"));
    }
    let dir = app.path().app_data_dir().map_err(|e| e.to_string())?;
    fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    Ok(dir.join(name))
}

/// Returns the file content, or None if it does not exist yet.
#[tauri::command]
fn read_app_file(app: tauri::AppHandle, name: String) -> Result<Option<String>, String> {
    let path = app_file(&app, &name)?;
    match fs::read_to_string(&path) {
        Ok(text) => Ok(Some(text)),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => Ok(None),
        Err(e) => Err(e.to_string()),
    }
}

/// Writes through a temporary file and a rename, so a crash never leaves half a file.
#[tauri::command]
fn write_app_file(app: tauri::AppHandle, name: String, content: String) -> Result<(), String> {
    let path = app_file(&app, &name)?;
    let tmp = path.with_extension("json.tmp");
    fs::write(&tmp, content).map_err(|e| e.to_string())?;
    fs::rename(&tmp, &path).map_err(|e| e.to_string())
}

/// Requests a window size in logical pixels; the UI checks the result and corrects it,
/// since platforms differ in whether the title bar is counted.
#[tauri::command]
fn fit_window(window: tauri::WebviewWindow, width: f64, height: f64) -> Result<(), String> {
    window
        .set_size(tauri::LogicalSize::new(width, height))
        .map_err(|e| e.to_string())
}

/// Day files of the old TimeTracker (`YYYY-MM-DD.json`) in a folder the user picked.
#[tauri::command]
fn read_legacy_dir(path: String) -> Result<Vec<(String, String)>, String> {
    let mut files = Vec::new();
    for entry in fs::read_dir(Path::new(&path)).map_err(|e| e.to_string())? {
        let entry = entry.map_err(|e| e.to_string())?;
        let name = entry.file_name().to_string_lossy().to_string();
        if is_day_file(&name) && entry.path().is_file() {
            let text = fs::read_to_string(entry.path()).map_err(|e| e.to_string())?;
            files.push((name, text));
        }
    }
    files.sort();
    Ok(files)
}

fn is_day_file(name: &str) -> bool {
    let bytes = name.as_bytes();
    name.len() == 15
        && name.ends_with(".json")
        && bytes[..10]
            .iter()
            .enumerate()
            .all(|(i, b)| if i == 4 || i == 7 { *b == b'-' } else { b.is_ascii_digit() })
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            read_app_file,
            write_app_file,
            read_legacy_dir,
            fit_window
        ])
        .run(tauri::generate_context!())
        .expect("error while running Tracker");
}

#[cfg(test)]
mod tests {
    use super::is_day_file;

    #[test]
    fn day_files_are_recognised() {
        assert!(is_day_file("2024-06-28.json"));
        assert!(!is_day_file("user_settings.json"));
        assert!(!is_day_file("2024-06-28.json.bak"));
        assert!(!is_day_file("2024_06_28.json"));
    }
}

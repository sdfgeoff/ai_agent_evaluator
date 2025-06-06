use std::fs::{self, File};
use std::io::{self};
use std::path::Path;
use zip::ZipWriter;
use zip::write::SimpleFileOptions;

pub fn zip_folder(src_folder: &str, dest_zip: &str) -> io::Result<()> {
    let src_path = Path::new(src_folder);
    let file = File::create(dest_zip)?;
    let mut zip = ZipWriter::new(file);

    let options = SimpleFileOptions::default()
        .compression_method(zip::CompressionMethod::Deflated)
        .unix_permissions(0o755);

    fn add_directory(
        path: &Path,
        base_path: &Path,
        zip: &mut ZipWriter<File>,
        options: SimpleFileOptions,
    ) -> io::Result<()> {
        for entry in fs::read_dir(path)? {
            let entry = entry?;
            let entry_path = entry.path();
            let name = entry_path
                .strip_prefix(base_path)
                .unwrap()
                .to_str()
                .unwrap();

            if entry_path.is_file() {
                let mut file = File::open(&entry_path)?;
                zip.start_file(name, options)?;
                io::copy(&mut file, zip)?;
            } else if entry_path.is_dir() {
                zip.add_directory(name.to_string(), options)?;
                add_directory(&entry_path, base_path, zip, options)?;
            }
        }
        Ok(())
    }

    add_directory(src_path, src_path, &mut zip, options)?;
    zip.finish()?;
    Ok(())
}

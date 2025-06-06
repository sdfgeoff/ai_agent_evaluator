use headless_chrome::{
    Browser, LaunchOptionsBuilder, protocol::cdp::Page::CaptureScreenshotFormatOption,
};
use std::fs;

pub fn capture_screenshot(
    input_url: &str,
    output_path: &str,
) -> Result<(), Box<dyn std::error::Error>> {
    // Open a new instance of Chrome
    let options = LaunchOptionsBuilder::default()
        // Make the window bigger
        .window_size(Some((1920, 1080)))
        .build()?;

    // Open a new instance of Chrome with the specified
    // options
    let browser = Browser::new(options)?;

    // Chrome always opens with one tab open, so
    // you just get that initial tab.
    let tab = browser.new_tab()?;

    // Navigate to the website and wait for it to
    // finish loading
    tab.navigate_to(input_url)?;
    tab.wait_until_navigated()?;

    // Screenshot the page to a PNG file and return
    // the bytes for that PNG
    let png_data = tab.capture_screenshot(CaptureScreenshotFormatOption::Png, None, None, true)?;

    // Save the bytes to the specified output file
    fs::write(output_path, png_data)?;

    Ok(())
}

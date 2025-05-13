use http_body_util::Empty;
use hyper::Request;
use hyper::body::Bytes;
use hyper_util::rt::TokioIo;
use tokio::net::TcpStream;

use http_body_util::BodyExt;
use serde::{Deserialize, Serialize};

mod llm_api;
use llm_api::types::ToolFunctionType;



#[derive(Serialize, Deserialize, Debug)]
struct MyBody {
    origin: String,
}


#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    // This is where we will setup our HTTP client requests.

    // Parse our URL...
    let url = "http://httpbin.org/ip".parse::<hyper::Uri>()?;

    // Get the host and the port
    let host = url.host().expect("uri has no host");
    let port = url.port_u16().unwrap_or(80);

    let address = format!("{}:{}", host, port);

    // Open a TCP connection to the remote host
    let stream = TcpStream::connect(address).await?;

    // Use an adapter to access something implementing `tokio::io` traits as if they implement
    // `hyper::rt` IO traits.
    let io = TokioIo::new(stream);

    // Create the Hyper client
    let (mut sender, conn) = hyper::client::conn::http1::handshake(io).await?;

    // Spawn a task to poll the connection, driving the HTTP state
    tokio::task::spawn(async move {
        if let Err(err) = conn.await {
            println!("Connection failed: {:?}", err);
        }
    });

    // The authority of our URL will be the hostname of the httpbin remote
    let authority = url.authority().unwrap().clone();

    // Create an HTTP request with an empty body and a HOST header
    let req = Request::builder()
        .uri(url)
        .header(hyper::header::HOST, authority.as_str())
        .body(Empty::<Bytes>::new())?;

    // Await the response...
    let mut res = sender.send_request(req).await?;

    println!("Response status: {}", res.status());

    // Collect the body into a single buffer
    let body_bytes = res.body_mut().collect().await?.to_bytes();

    // Deserialize the JSON response into the MyBody struct
    let as_str = std::str::from_utf8(&body_bytes)?;
    let my_body: MyBody = serde_json::from_str(as_str)?;

    // Print the deserialized struct
    println!("Deserialized response: {:?}", my_body);

    Ok(())
}

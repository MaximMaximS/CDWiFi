use reqwest::{blocking::Client, redirect::Policy, Url};
use scraper::Html;
use std::time::Duration;

fn main() -> anyhow::Result<()> {
    let client = Client::builder()
        .redirect(Policy::none())
        .timeout(Duration::from_secs(5))
        .build()?;

    let res = client.get("http://www.example.com").send()?;

    let location = res.headers().get("Location");

    if !res.status().is_redirection() || location.is_none() {
        if res.status().is_success() {
            println!("Already connected to the internet");
            return Ok(());
        }
        anyhow::bail!("Failed to get capnet address");
    }

    let location = Url::parse(
        location
            .ok_or_else(|| anyhow::anyhow!("Failed to get Location header"))?
            .to_str()?,
    )?;

    let res = client.get(location.clone()).send()?;

    let text = res.text()?;

    let document = Html::parse_document(&text);

    let secret = document
        .select(&scraper::Selector::parse("input[name=secret]").unwrap())
        .next()
        .ok_or_else(|| anyhow::anyhow!("Failed to get secret element"))?
        .attr("value")
        .ok_or_else(|| anyhow::anyhow!("Failed to get secret value"))?;

    let payload = format!("secret={secret}&eula=on");

    let res = client
        .post(location.join("/accept")?)
        .header("Content-Type", "application/x-www-form-urlencoded")
        .body(payload)
        .send()?;

    if !res.status().is_redirection() {
        anyhow::bail!("Failed to connect!");
    }

    println!("Connected successfully!");

    Ok(())
}

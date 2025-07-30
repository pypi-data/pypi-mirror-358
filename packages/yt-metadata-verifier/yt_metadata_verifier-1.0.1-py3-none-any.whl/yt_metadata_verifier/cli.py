import argparse
import json
import yt_dlp
import logging
from importlib.metadata import version, PackageNotFoundError

PACKAGE_NAME = "yt-metadata-verifier"

logger = logging.getLogger("yt-verify")


def fetch_actual_metadata(video_url):
    try:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": True,
            "postprocessors": [],
            "format": "bestaudio/best",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
        if info is not None:
            video_title = info.get("fulltitle")
            video_display_id = info.get("display_id")
            video_original_url = f"https://www.youtube.com/watch?v={video_display_id}"
            video_tag = info.get("tags")
            video_duration = info.get("duration_string")
            channel_name = info.get("uploader")
            channel_url = info.get("uploader_url")

            return {
                "success": True,
                "data": {
                    "title": video_title,
                    "url": video_original_url,
                    "duration": video_duration,
                    "tags": video_tag,
                    "channel": {"name": channel_name, "url": channel_url},
                },
            }

    except Exception as e:
        return {"success": False, "error": str(e), "url": video_url}


def main():
    try:
        cli_version = version(PACKAGE_NAME)
    except PackageNotFoundError:
        cli_version = "0.0.0-dev"

    parser = argparse.ArgumentParser(
        description="📺 YouTube Metadata Verifier\n\n"
        "Fetch and correct YouTube video metadata (title, channel name, and channel URL).\n"
        "Useful for validating or cleaning up content.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--json", required=True, help="Input JSON file (list of {'url': ...})"
    )
    parser.add_argument(
        "--output", default="corrected.json", help="Output file for corrected metadata"
    )
    parser.add_argument(
        "--errors",
        default="errors.json",
        help="Output file for failed metadata fetches",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s v{cli_version}"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    try:
        with open(args.json, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    except Exception as e:
        logger.error(f"❌ Failed to read input JSON: {e}")
        return

    corrected = []
    errors = []

    for i, entry in enumerate(input_data, 1):
        url = entry.get("url")
        if not url:
            logger.warning(f"⚠️ Skipping entry {i}: missing 'url'")
            errors.append({"entry": entry, "error": "Missing 'url'"})
            continue

        logger.info(f"🔍 [{i}] Processing: {url}")
        result = fetch_actual_metadata(url)
        if result is not None:
            if result["success"]:
                corrected.append(result["data"])
            else:
                logger.error(f"❌ [{i}] Failed: {result['error']}")
                errors.append(result)

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(corrected, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Corrected metadata written to {args.output}")
    except Exception as e:
        logger.error(f"❌ Failed to write corrected file: {e}")

    if errors:
        try:
            with open(args.errors, "w", encoding="utf-8") as f:
                json.dump(errors, f, indent=2, ensure_ascii=False)
            logger.warning(f"⚠️ {len(errors)} errors written to {args.errors}")
        except Exception as e:
            logger.error(f"❌ Failed to write errors file: {e}")
    else:
        logger.info("🎉 All videos processed successfully with no errors.")

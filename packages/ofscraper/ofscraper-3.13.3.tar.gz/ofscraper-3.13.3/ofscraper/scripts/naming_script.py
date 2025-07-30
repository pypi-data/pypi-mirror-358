import logging
import json
import subprocess
import traceback
import arrow
import ofscraper.utils.settings as settings
import ofscraper.utils.config.data as config_data
import ofscraper.main.open.run as run


def naming_script(dir, file, ele):
    log = logging.getLogger("shared")

    if not settings.get_settings().naming_script:
        return

    script_path = settings.get_settings().naming_script
    if not script_path:
        log.error("Naming script path is not configured. Aborting naming script.")
        return

    log.debug(f"Attempting to run naming script: {script_path}")

    try:
        media_payload = ele.media
        post_payload = ele.post.post

        payload_data = {
            "media": media_payload,
            "post": post_payload,
            "dir": str(dir),
            "file": str(file),
            "dir_format": config_data.get_dirformat(),
            "file_format": config_data.get_fileformat(),
            "metadata": config_data.get_metadata(),
            "username": ele.username,
            "model_id": ele.model_id,
            "post_id": ele.postid,
            "media_id": ele.id,
            "media_type": ele.mediatype.capitalize(),
            "value": ele.value.capitalize(),
            "date": arrow.get(ele.postdate).format(config_data.get_date()),
            "response_type": ele.modified_responsetype,
            "label": ele.label_string,
            "download_type": ele.downloadtype,
        }

        input_json_str = json.dumps(payload_data, indent=None, ensure_ascii=False)

        result = run(
            [script_path],
            input=input_json_str.encode(
                "utf-8"
            ),  # Pass the JSON string as stdin (encoded to bytes)
            capture_output=True,
            text=True,  # Decode stdout/stderr as text
            check=True,  # Raise CalledProcessError for non-zero exit codes
        )
        final_result = result.stdout.strip()

        log.debug(f"Naming script stdout: {final_result}")
        if result.stderr:
            log.warning(f"Naming script stderr: {result.stderr.strip()}")
        log.debug("Naming script ran successfully via stdin.")
        return final_result

    except FileNotFoundError:
        log.error(
            f"Naming script executable not found: '{script_path}'. Please ensure the path is correct and the script is executable."
        )
    except subprocess.CalledProcessError as e:
        log.error(
            f"Naming script failed with exit code {e.returncode}: '{script_path}'"
        )
        log.error(f"Naming script stdout:\n{e.stdout.strip()}")
        log.error(f"Naming script stderr:\n{e.stderr.strip()}")
    except json.JSONDecodeError as e:
        log.error(f"Failed to serialize payload to JSON for naming script: {e}")
    except Exception as e:
        log.critical(
            f"An unexpected error occurred while running naming script '{script_path}': {e}",
            exc_info=True,
        )
        log.critical(
            f"An unexpected error occurred while running final script with script '{script_path}': {e}",
            exc_info=True,
        )
        log.traceback_(e)
        log.traceback_(traceback.format_exc())

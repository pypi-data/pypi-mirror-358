import threading
from dotenv import load_dotenv
import ofscraper.utils.ads as ads
import ofscraper.utils.args.accessors.read as read_args
import ofscraper.utils.args.mutators.write as write_args

import ofscraper.utils.config.data as config_data
import ofscraper.utils.of_env.of_env as of_env
from ofscraper.utils.args.accessors.areas import get_text_area


# --- Globals for one-time initialization ---
_env_loaded = False
_init_lock = threading.Lock()


def _load_env_once():
    """
    Loads all environment-based configurations once.
    This function is thread-safe and ensures that config files are read
    and processed only one time during the application's lifecycle.
    """
    global _env_loaded
    # Quick check to avoid locking if already loaded
    if _env_loaded:
        return

    with _init_lock:
        # Double-check inside the lock to handle race conditions
        if _env_loaded:
            return
        # Load .env file if it exists
        load_dotenv(override=True)
        _env_loaded = True


# --- Main Settings Logic ---
settings = {}


def get_args():
    return read_args.retriveArgs()


def update_args(args):
    global settings
    write_args.setArgs(args)
    settings = setup_settings()


def get_settings():
    global settings
    _load_env_once()  # Ensures env is populated before settings are first calculated.
    if not settings:
        with _init_lock:
            # Check again inside lock for thread safety
            if not settings:
                settings = setup_settings()
    return settings


def setup_settings():
    merged = read_args.retriveArgs()
    merged.key_mode = read_args.retriveArgs().key_mode or config_data.get_key_mode()
    merged.cache_disabled = (
        read_args.retriveArgs().no_cache or config_data.get_cache_mode() == "disabled"
    )
    merged.api_cached_disabled = (
        read_args.retriveArgs().no_cache
        or read_args.retriveArgs().no_api_cache
        or config_data.get_cache_mode() == "api_disabled"
    )
    merged.dynamic_rules = (
        read_args.retriveArgs().dynamic_rules or config_data.get_dynamic()
    )
    merged.download_bars = (
        read_args.retriveArgs().downloadbars or config_data.get_show_downloadprogress()
    )
    merged.discord_level = (
        read_args.retriveArgs().discord_level or config_data.get_discord()
    )
    merged.log_level = read_args.retriveArgs().log_level or of_env.getattr(
        "DEFAULT_LOG_LEVEL"
    )
    merged.trunicate = get_trunication()
    merged.userlist = get_userlist()
    merged.blacklist = get_blacklist()
    merged.text_type = read_args.retriveArgs().text_type or config_data.get_textType()
    merged.space_replacer = (
        read_args.retriveArgs().space_replacer or config_data.get_spacereplacer()
    )
    merged.text_length = (
        read_args.retriveArgs().text_length or config_data.get_textlength()
    )
    merged.size_max = read_args.retriveArgs().size_max or config_data.get_filesize_max()
    merged.size_min = read_args.retriveArgs().size_min or config_data.get_filesize_min()
    merged.download_sems = (
        read_args.retriveArgs().downloadsem or config_data.get_download_semaphores()
    )
    merged.max_post_count = (
        read_args.retriveArgs().max_count or config_data.get_max_post_count()
    )
    merged.mediatypes = read_args.retriveArgs().mediatype or config_data.get_filter()
    merged.private_key = (
        read_args.retriveArgs().private_key or config_data.get_private_key()
    )
    merged.client_id = read_args.retriveArgs().client_id or config_data.get_client_id()
    merged.download_limit = get_download_limit()
    merged.length_max = get_max_length()
    merged.length_min = get_min_length()
    merged.neg_filter = get_neg_filter()
    merged.hash = config_data.get_hash()
    merged.post_script = (
        read_args.retriveArgs().post_script or config_data.get_post_script()
    )
    merged.download_script = (
        read_args.retriveArgs().download_script
        or config_data.get_post_download_script()
    )
    merged.naming_script = (
        read_args.retriveArgs().naming_script or config_data.get_naming_script()
    )
    merged.download_skip_script = (
        read_args.retriveArgs().download_skip_script
        or config_data.get_skip_download_script()
    )
    merged.auto_resume = get_auto_resume()
    merged.auto_after = get_auto_after_enabled()
    merged.cached_disabled = get_cached_disabled()
    merged.logs_expire_time = config_data.get_logs_expire()
    merged.ssl_verify = config_data.get_ssl_verify()

    return merged


def get_download_text():
    return (
        get_text_area()
        or read_args.retriveArgs().text
        or read_args.retriveArgs().text_only
    )


def get_ffmpeg():
    return config_data.get_ffmpeg() or ""


def get_auto_after_enabled():
    if get_cached_disabled():
        return False
    return config_data.get_enable_after()


def get_cached_disabled():
    if read_args.retriveArgs().no_cache:
        return True
    if read_args.retriveArgs().no_api_cache:
        return True
    return False


def get_auto_resume():
    if read_args.retriveArgs().no_auto_resume:
        return False
    return config_data.get_part_file_clean()


def get_neg_filter():
    neg = read_args.retriveArgs().neg_filter or []
    if read_args.retriveArgs().block_ads or config_data.get_block_ads():
        neg.append(ads.get_ad_key_words())
    return neg


def get_min_length():
    if read_args.retriveArgs().length_min is not None:
        return read_args.retriveArgs().length_min
    return config_data.get_min_length()


def get_max_length():
    if read_args.retriveArgs().length_max is not None:
        return read_args.retriveArgs().length_max
    return config_data.get_max_length()


def get_download_limit():
    out = read_args.retriveArgs().download_limit or config_data.get_download_limit()
    return max(out, 1024) if out else out


def get_trunication():
    if read_args.retriveArgs().original:
        return False
    return config_data.get_truncation()


def get_userlist():
    out = read_args.retriveArgs().user_list or config_data.get_default_userlist()
    if isinstance(out, str):
        out = out.split(",")
    return out


def get_blacklist():
    out = read_args.retriveArgs().black_list or config_data.get_default_blacklist()
    if isinstance(out, str):
        out = out.split(",")
    return out

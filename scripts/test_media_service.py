from scripts.media_service import MAX_UPLOAD_BYTES, MediaError, _magic_mime, _target_key


def test_media_magic_bytes_are_strict():
    assert _magic_mime(b"\xff\xd8\xffJPEG") == "image/jpeg"
    assert _magic_mime(b"\x89PNG\r\n\x1a\nPNG") == "image/png"
    assert _magic_mime(b"RIFF0000WEBP") == "image/webp"
    try:
        _magic_mime(b"MZnot-an-image")
    except MediaError:
        pass
    else:
        raise AssertionError("Non-image magic bytes must be rejected.")


def test_media_target_keys_never_use_client_filename():
    media_id = "4f57e0d5-5d0b-4cc9-9f8b-000000000001"
    key = _target_key("DISPUTE", "dispute-123", media_id)
    assert key == f"disputes/dispute-123/evidence/{media_id}.webp"
    assert "php" not in key.lower()
    assert ".." not in key


def test_media_upload_limit_is_five_megabytes():
    assert MAX_UPLOAD_BYTES == 5 * 1024 * 1024

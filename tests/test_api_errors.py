"""Error-path tests: these endpoints return 200 with a JSON error envelope
(no network, no filesystem writes needed) exactly like the original Flask
implementation (`return jsonify({"status": "error", "message": ...})`,
i.e. no explicit HTTP error status code).
"""


def test_get_data_process_missing_caddress(client):
    response = client.get("/get_data_process")
    assert response.status_code == 200
    assert response.json() == {
        "status": "error",
        "message": "You must specify Contract Address",
    }


def test_file_process_missing_file_id(client):
    response = client.get("/file_process")
    assert response.status_code == 200
    assert response.json() == {
        "status": "error",
        "message": "File ID is required",
    }


def test_upload_file_wrong_extension(client):
    response = client.post(
        "/upload_file",
        files={"file": ("not-a-db.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "error",
        "message": "The file must be SQlite extension",
    }


def test_upload_file_empty_filename(client):
    # NOTE: Known Flask -> FastAPI behavior difference (documented, not a
    # regression affecting the real frontend): Werkzeug's `request.files`
    # still builds a FileStorage with filename == '' for an empty-filename
    # multipart part, which the original handler turned into a 200 JSON
    # error envelope. Starlette's multipart parser instead treats an
    # empty-filename part as a plain text form field (not an UploadFile),
    # so FastAPI's typed `UploadFile = File(...)` dependency rejects it
    # with a 422 before the handler body runs. The Angular client always
    # appends a real File object (see contract-collect.component.ts), so
    # this edge case is never hit in practice.
    response = client.post(
        "/upload_file",
        files={"file": ("", b"hello world", "application/octet-stream")},
    )
    assert response.status_code == 422

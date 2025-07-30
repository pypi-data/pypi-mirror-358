from huggingface_hub import HfApi


api = HfApi(token="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")
api.upload_large_folder(
    folder_path="/mnt/data2/bingkui/mcha_pypi/dataset",
    repo_id="tbbbk/mcha_tmp",
    repo_type="dataset",
)

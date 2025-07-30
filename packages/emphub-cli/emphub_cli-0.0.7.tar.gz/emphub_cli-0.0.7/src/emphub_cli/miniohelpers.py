from minio import Minio


def getClient(config):
    client = Minio(
        endpoint=config["registry"]["host"],
        access_key=config["registry"]["access_key"],
        secret_key=config["registry"]["secret_key"],
        secure=config["registry"]["secure"]
    )
    return client

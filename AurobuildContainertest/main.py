import docker

client = docker.from_env()

# Указываем имя образа и путь к Dockerfile
image_name = "test_image"
dockerfile_path = "/home/fargus/testcontainer"

# Сборка образа
client.images.build(
    path=dockerfile_path,
    tag=image_name
)
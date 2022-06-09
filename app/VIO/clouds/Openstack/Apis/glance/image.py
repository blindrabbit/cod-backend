def create_image(url, name, disk_format, container_format, visibility, conn):
    image_attrs = {
    'name': name,
    'disk_format': disk_format,
    'container_format': container_format,
    'visibility': visibility,
    }

    attrs = conn.image.create_image(**image_attrs)
    image = conn.image.import_image(attrs, method="web-download", uri=url)
    
    return image
# # Url where glance can download the image
# uri = 'https://download.cirros-cloud.net/0.4.0/cirros-0.4.0-x86_64-disk.img'
# # Build the image attributes and import the image.
# image_attrs = {
#     'name': EXAMPLE_IMAGE_NAME,
#     'disk_format': 'qcow2',
#     'container_format': 'bare',
#     'visibility': 'public',
#     }

# image = conn.image.create_image(**image_attrs)
# conn.image.import_image(image, method="web-download", uri=uri)




# EXAMPLE_IMAGE_NAME = "example_image"

# print("List Images:")
# for image in conn.image.images():
#     print(image.name)

# print("Delete Image:")
# example_image = conn.image.find_image(EXAMPLE_IMAGE_NAME)
# conn.image.delete_image(example_image, ignore_missing=False)



# # del image 



# EXAMPLE_IMAGE_NAME = "example_image"

# print("List Images:")
# for image in conn.image.images():
#     print(image.name)

# print("Delete Image:")
# example_image = conn.image.find_image(EXAMPLE_IMAGE_NAME)
# conn.image.delete_image(example_image, ignore_missing=False)
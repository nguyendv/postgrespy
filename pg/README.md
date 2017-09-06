This directory provides a Postgres container for testing `postgrespy`.

How to manually build this image?
`bash build.sh`. It also uploads the image to the Gitlab registry.

How to manually run this container?
`bash run.sh`

How to upload to pypi?
`bash pypi-upload.sh`

# Release notes
## Version 0.2.2
- Add support for JSONB[] type

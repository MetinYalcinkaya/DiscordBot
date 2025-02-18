if [ -t 1 ]; then
  INTERACTIVE="-it"
else
  INTERACTIVE=""
fi

docker run \
  --rm \
  --volume .:/app \
  --volume /app/.venv \
  $INTERACTIVE \
  $(docker build -q .) \
  "$0"

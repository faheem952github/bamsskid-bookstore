#!/bin/bash

echo "⏳ -- Waiting for Postgres to be ready..."

until pg_isready -h db -p 5432 -U "$POSTGRES_USER"; do
  sleep 2
done

echo "✅ -- Postgres is ready."

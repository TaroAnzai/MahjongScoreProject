FROM python:3.12-slim AS schema
WORKDIR /backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
# Generate from this checkout, without contacting a live API or database.
RUN DATABASE_URL=sqlite:///:memory: OPENAPI_URL_PREFIX=/doc python -c 'from app import create_app; import json; app = create_app("testing"); response = app.test_client().get("/doc/openapi.json"); assert response.status_code == 200; open("/openapi.json", "w").write(json.dumps(response.json))'

FROM node:22-slim AS development
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM development AS build
COPY --from=schema /openapi.json /openapi.json
RUN ORVAL_API_URL=/openapi.json npm run orval
ARG VITE_API_BASE_URL
ARG VITE_RECAPTCHA_SITE_KEY
ARG VITE_SHARE_ORIGIN
ENV VITE_USE_HTTPS=false
RUN npm run build

FROM nginx:stable-alpine AS production
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html/mahjong

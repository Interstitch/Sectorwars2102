# Sectorwars2102 Startup Guide

## Quick Start After Codespace Boot

After starting your GitHub Codespace, run this single command to verify everything is healthy:

```bash
./dev-scripts/startup-health-check.sh
```

This will check:
- ✅ All Docker services are running
- ✅ All services report healthy status
- ✅ API endpoints are accessible
- ✅ Database connection is working
- ✅ Frontend applications are responding

## Expected Output

If everything is healthy, you'll see:
```
✓ All systems operational!

Admin Panel: http://localhost:3001
Player Client: http://localhost:3000
API Docs: http://localhost:8080/docs
```

## Troubleshooting

### Unhealthy Services

If a service shows as unhealthy:

1. Check the logs:
```bash
docker-compose logs <service-name>
```

2. Restart the service:
```bash
docker-compose restart <service-name>
```

3. If the issue persists, check for import errors or missing dependencies

### Failed Services

If a service isn't running at all:

1. Start all services:
```bash
docker-compose up -d
```

2. Check for errors during startup:
```bash
docker-compose logs <service-name>
```

### Common Issues

**Gameserver Import Errors**
- **Symptom**: Gameserver shows as unhealthy, logs show `ModuleNotFoundError`
- **Solution**: Check recent code changes for incorrect imports. The gameserver auto-reloads on code changes, so a syntax/import error will cause it to crash.

**Database Connection Failures**
- **Symptom**: Database endpoint returns 500
- **Solution**: Check that the Neon database is accessible and credentials in `.env` are correct

**Port Conflicts**
- **Symptom**: Services fail to start with "port already in use"
- **Solution**: Kill any processes using the ports:
```bash
lsof -ti:8080,3000,3001,5433,6379 | xargs kill -9
docker-compose down && docker-compose up -d
```

## Manual Service Management

### Start All Services
```bash
./dev-scripts/start-unified.sh
```
or
```bash
docker-compose up -d
```

### Stop All Services
```bash
docker-compose down
```

### Restart a Specific Service
```bash
docker-compose restart <service-name>
```

Services:
- `gameserver` - FastAPI backend (port 8080)
- `player-client` - React frontend (port 3000)
- `admin-ui` - Admin panel (port 3001)
- `database` - PostgreSQL (port 5433)
- `redis-cache` - Redis (port 6379)
- `nginx-gateway` - Nginx reverse proxy (port 80/443)

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f <service-name>

# Last 50 lines
docker-compose logs --tail=50 <service-name>
```

## Database Operations

### Run Migrations
```bash
docker-compose exec gameserver poetry run alembic upgrade head
```

### Create New Migration
```bash
docker-compose exec gameserver poetry run alembic revision -m "description"
```

### Check Migration Status
```bash
docker-compose exec gameserver poetry run alembic current
```

## Testing

### Run Backend Tests
```bash
docker-compose exec gameserver poetry run pytest
```

### Run E2E Tests
```bash
npx playwright test -c e2e_tests/playwright.config.ts
```

### Run Frontend Tests
```bash
docker-compose exec player-client npm test
```

## Development Workflow

### Typical Codespace Startup Routine

1. **Open Codespace** - GitHub will auto-start Docker containers

2. **Run Health Check**
   ```bash
   ./dev-scripts/startup-health-check.sh
   ```

3. **If Everything is Green**: Start coding! 🚀

4. **If Issues Found**: Follow troubleshooting steps above

### Before Shutting Down Codespace

1. **Check for uncommitted changes**:
   ```bash
   git status
   ```

2. **Commit your work**:
   ```bash
   git add -A
   git commit -m "feat: description of changes"
   git push origin master
   ```

3. **Optional: Stop services to free resources**:
   ```bash
   docker-compose down
   ```

## URL Reference

- **Admin Panel**: http://localhost:3001
- **Player Client**: http://localhost:3000
- **API Docs**: http://localhost:8080/docs
- **API Health**: http://localhost:8080/api/v1/status/health
- **Database**: postgresql://localhost:5433 (or external Neon)
- **Redis**: redis://localhost:6379

## Environment Variables

Critical environment variables are loaded from `.env`:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Authentication secret
- `ADMIN_USERNAME` / `ADMIN_PASSWORD` - Admin credentials
- PayPal/OAuth credentials (optional for development)

**Never commit `.env` to git!** It contains secrets and is in `.gitignore`.

## Help & Documentation

- **API Documentation**: http://localhost:8080/docs (Swagger UI)
- **Project Docs**: `/DOCS/` directory
- **Development Scripts**: `/dev-scripts/` directory

---

## Automation Ideas for Future

- [ ] Add `.devcontainer/postCreateCommand.sh` to auto-run health check
- [ ] Add pre-commit hooks to ensure code quality
- [ ] Add automated dependency updates via Dependabot
- [ ] Add GitHub Actions for CI/CD testing

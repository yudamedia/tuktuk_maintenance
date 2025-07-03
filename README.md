# TukTuk Management System

## Related Apps
This app works with the TukTuk Maintenance System:
- Repository: https://github.com/yudamedia/tuktuk-maintenance
- Integration: API calls between systems for maintenance scheduling

## Installation
```bash
# Install both apps
bench get-app https://github.com/yudamedia/tuktuk-management.git
bench get-app https://github.com/yudamedia/tuktuk-maintenance.git

# Install on site
bench --site yoursite install-app tuktuk_management
bench --site yoursite install-app tuktuk_maintenance
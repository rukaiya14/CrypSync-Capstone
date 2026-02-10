# CrypSync - Real-Time Cryptocurrency Tracker

A modern, scalable Flask-based web application for tracking cryptocurrency prices in real-time with multi-role access, portfolio management, advanced analytics, and comprehensive admin features.

> 📚 **New to CrypSync?** Check out [INDEX.md](INDEX.md) for a complete documentation guide.

> 🚀 **Quick Start**: See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for setup guide.

> 🔐 **Admin Panel**: See [ADMIN_GUIDE.md](ADMIN_GUIDE.md) for admin documentation.

## Features

### Core Functionality

**Real-Time Price Tracking**: Live cryptocurrency prices updated every 60 seconds from CoinGecko API

**Multi-Role System**: Three distinct user experiences
- **User Role**: Portfolio management and trading
- **Analyst Role**: Research tools with multi-coin comparison
- **Admin Role**: System management and monitoring

**User Authentication**: Secure JWT-based authentication with bcrypt password hashing (12 salt rounds)

**Portfolio Management**: Track cryptocurrency holdings with buy/sell transactions and profit/loss analysis

**Price Alerts**: Set custom price thresholds with real-time monitoring

**Historical Analysis**: Interactive charts with 7, 30, 90, 180, and 365-day views

**Live Search**: Filter and search through 50+ tracked cryptocurrencies

**Admin Panel**: Comprehensive system management with user and coin administration

### User Interface

- Clean, responsive dark theme inspired by CoinStats
- Real-time price updates without page refresh
- Interactive sparkline charts using Canvas API
- Mobile-friendly responsive layout with Bootstrap 5.3.0
- Professional dashboards for each user role
- Real-time system health monitoring

## Technology Stack

### Backend
- **Python Flask 2.3.3** - Web framework
- **SQLite** - Database for persistent storage
- **JWT Tokens** - Secure authentication with 24-hour expiration
- **bcrypt** - Password hashing with 12 salt rounds
- **Requests 2.31.0** - API calls to CoinGecko

### Frontend
- **HTML5 & CSS3** - Modern semantic markup
- **Bootstrap 5.3.0** - Responsive UI framework
- **JavaScript (ES6+)** - Dynamic interactions
- **Chart.js 4.3.0** - Data visualization
- **Font Awesome 6.4.0** - Icon library

### Data Source
- **CoinGecko API v3** - Real-time cryptocurrency data
- Rate limit: 50 requests/minute
- Caching and rate limiting implemented

### AWS Integration (Optional)
- **AWS Elastic Beanstalk** - Application hosting
- **DynamoDB** - Scalable NoSQL database
- **CloudWatch** - Monitoring and logging
- **SES** - Email notifications

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Start (3 Steps)

1. **Clone the repository**
```bash
git clone <repository-url>
cd crypsync
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Access the application**
- Open your browser and go to: **http://localhost:5000**
- Admin credentials: `admin@crypsync.com` / `admin123`
- Or create a new user account via registration

### Database Setup

The database is automatically initialized on first run. To manually set up:

```bash
# Initialize database
python migrate_database.py

# Create admin user
python -c "from database import create_admin_user; create_admin_user()"

# Verify setup
python verify_setup.py
```

## Project Structure

```
CrypSync/
├── app.py                          # Main Flask application
├── database.py                     # SQLite database management
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── services/                       # Business logic services
│   ├── auth_service.py            # User authentication
│   ├── price_service.py           # CoinGecko API integration
│   ├── alert_service.py           # Price alerts
│   ├── portfolio_service_db.py    # Portfolio management
│   ├── historical_service.py      # Historical data
│   ├── admin_service.py           # Admin operations
│   ├── system_service.py          # System monitoring
│   └── visualization_service.py   # Chart data preparation
├── templates/                      # HTML templates
│   ├── base.html                  # Base template with navbar
│   ├── login.html                 # Login page with role selection
│   ├── register.html              # Registration page
│   ├── home.html                  # Public homepage
│   ├── dashboard.html             # User dashboard
│   ├── analyst_dashboard.html     # Analyst research tools
│   ├── admin_dashboard.html       # Admin management console
│   ├── portfolio.html             # Portfolio tracking
│   ├── trading.html               # Buy/sell interface
│   ├── alerts.html                # Price alerts
│   ├── historical.html            # Historical charts
│   └── about.html                 # About page
└── static/                         # Static assets
    ├── css/
    │   └── style.css              # Custom styles
    └── js/
        ├── crypto-tracker.js      # Main tracking functionality
        ├── dashboard.js           # Dashboard interactions
        ├── login.js               # Login handling
        └── historical.js          # Chart rendering
```

## Usage

### For Regular Users

1. **Sign up** for a new account or use existing credentials
2. **Select "User" role** at login for portfolio management
3. **View Dashboard** to see live cryptocurrency prices and your portfolio
4. **Add Holdings** via Portfolio page to track your investments
5. **Set Price Alerts** to get notified when prices reach thresholds
6. **Trade Cryptocurrencies** using the Trading page
7. **View Historical Data** with interactive charts

### For Analysts

1. **Login** with "Analyst" role selection
2. **Access Analyst Dashboard** for research tools
3. **Compare Multiple Coins** with normalized price charts
4. **Analyze Correlations** between different cryptocurrencies
5. **Custom Date Ranges** for historical analysis (7, 30, 90, 180, 365 days)
6. **Volume Comparison** across selected cryptocurrencies

### For Administrators

1. **Login** with admin credentials: `admin@crypsync.com` / `admin123`
2. **Select "Admin" role** at login
3. **Access Admin Panel** from the orange "Admin" link in navbar
4. **Manage Users**: View all users, delete non-admin users
5. **Manage Coins**: Add/remove tracked cryptocurrencies
6. **Monitor System**: View real-time system health and API status
7. **Track Activity**: Monitor all transactions and user activity

## API Endpoints

### Public Endpoints
- `GET /` - Homepage
- `GET /about` - About page
- `GET /login` - Login page
- `POST /login` - Process login with role selection
- `GET /register` - Registration page
- `POST /register` - Process registration

### User Endpoints (Authentication Required)
- `GET /dashboard` - User dashboard
- `GET /analyst` - Analyst dashboard
- `GET /portfolio` - Portfolio page
- `GET /trading` - Trading page
- `GET /alerts` - Price alerts page
- `GET /historical` - Historical charts
- `GET /api/prices` - Get current prices
- `GET /api/portfolio` - Get user portfolio
- `POST /api/portfolio/buy` - Buy cryptocurrency
- `POST /api/portfolio/sell` - Sell cryptocurrency
- `GET /api/historical` - Get historical data
- `POST /api/alerts` - Create price alert

### Admin Endpoints (Admin Role Required)
- `GET /admin` - Admin dashboard
- `GET /api/admin/users` - Get all users
- `GET /api/admin/statistics` - System statistics
- `GET /api/admin/coins` - Get tracked coins
- `POST /api/admin/coins/add` - Add coin to tracking
- `POST /api/admin/coins/remove` - Remove coin
- `GET /api/admin/transactions` - View all transactions
- `POST /api/admin/users/delete` - Delete user

### System Endpoints
- `GET /api/system/status` - System health status
- `GET /api/system/api-status` - API connection status

## Features in Detail

### Real-Time Price Updates
- Automatic refresh every 60 seconds
- Manual refresh button available
- Color-coded 24-hour change indicators
- Responsive price formatting
- Sparkline charts for 7-day trends

### Multi-Role System
- **User Dashboard**: Portfolio-focused with holdings and trading
- **Analyst Dashboard**: Research-focused with comparison tools
- **Admin Dashboard**: Management-focused with system monitoring
- Role selection at login
- Custom navigation per role

### Portfolio Management
- Add cryptocurrency holdings manually
- Track amount, purchase price, and current value
- Real-time profit/loss calculation
- Transaction history
- Portfolio snapshots for historical tracking

### Price Alert System
- Set alerts above or below current price
- Real-time monitoring
- Visual notifications
- Persistent alerts in database
- Email notifications (configurable)

### Historical Analysis
- Interactive Chart.js visualizations
- Multiple time periods: 7, 30, 90, 180, 365 days
- Cryptocurrency selector
- Normalized price comparison (Analyst role)
- Volume analysis

### User Management
- Secure password hashing with bcrypt
- JWT token-based sessions
- Role-based access control (user/analyst/admin)
- SQLite database storage
- Session management

### Admin Features
- User management dashboard
- Add/remove tracked cryptocurrencies
- Real-time system health monitoring
- API connection status
- Active users counter
- Transaction monitoring
- User statistics

## Database Schema

### Core Tables
- **users** - User accounts with roles
- **sessions** - Active user sessions
- **holdings** - Portfolio holdings
- **transactions** - Buy/sell transactions
- **portfolio_snapshots** - Historical portfolio values
- **portfolio_alerts** - Portfolio-level alerts
- **price_alerts** - Price threshold alerts
- **tracked_coins** - Admin-managed coin list
- **historical_prices** - Cached price data

See [DATABASE_GUIDE.md](DATABASE_GUIDE.md) for detailed schema documentation.

## Configuration

### Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
COINGECKO_API_KEY=your-api-key-here
```

### Default Configuration
- Secret Key: `dev-secret-key-change-in-production`
- Database: `crypsync.db` (SQLite)
- Port: `5000`
- Debug: `True` (development)

## Demo Credentials

### Admin Access
- **Email**: admin@crypsync.com
- **Password**: admin123
- **Role**: Admin (select at login)

### Regular User
- Create new account via registration page
- Select "User" or "Analyst" role at login

## Future Enhancements

### Planned Features
- [ ] WebSocket support for real-time price streaming
- [ ] Email alerts via AWS SES
- [ ] Advanced portfolio analytics
- [ ] Social features (share portfolios)
- [ ] Mobile app (React Native)
- [ ] Two-factor authentication
- [ ] API rate limiting per user
- [ ] Cryptocurrency news integration
- [ ] Market sentiment analysis
- [ ] Trading bot integration

### In Progress
- [x] Multi-role system
- [x] Portfolio tracking
- [x] Historical charts
- [x] Admin panel
- [x] System monitoring
- [ ] News feed integration
- [ ] Enhanced analytics

## Deployment

### Local Development
```bash
python app.py
```
Access at: http://localhost:5000

### AWS Elastic Beanstalk
```bash
# Deploy to AWS
./deploy-aws.sh

# Or manually
eb init
eb create crypsync-env
eb deploy
```

See [README_AWS.md](README_AWS.md) for detailed AWS deployment instructions.

## Testing

### Run Tests
```bash
# Test admin functionality
python test_admin.py

# Verify setup
python verify_setup.py
```

### Manual Testing
1. Register a new user
2. Login with different roles
3. Add portfolio holdings
4. Set price alerts
5. View historical charts
6. Test admin features

## Documentation

- **[INDEX.md](INDEX.md)** - Documentation index
- **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)** - Complete setup guide
- **[ADMIN_GUIDE.md](ADMIN_GUIDE.md)** - Admin panel documentation
- **[DATABASE_GUIDE.md](DATABASE_GUIDE.md)** - Database schema
- **[MULTI_ROLE_IMPLEMENTATION.md](MULTI_ROLE_IMPLEMENTATION.md)** - Multi-role system
- **[COMMANDS.md](COMMANDS.md)** - Command reference
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick reference guide

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Submit a pull request

## Security

- Passwords hashed with bcrypt (12 salt rounds)
- JWT tokens with 24-hour expiration
- Session-based authentication
- Role-based access control
- SQL injection prevention
- XSS protection
- CSRF protection (recommended for production)

## Performance

- API response caching
- Rate limiting (50 requests/minute)
- Database indexing
- Lazy loading
- Auto-refresh optimization
- Efficient queries

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions:
- Check the [documentation](INDEX.md)
- Run `python verify_setup.py` to check your setup
- Review [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for troubleshooting
- Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for common commands

## Acknowledgments

- **CoinGecko API** - Cryptocurrency data provider
- **Flask** - Web framework
- **Bootstrap** - UI framework
- **Chart.js** - Data visualization
- **Font Awesome** - Icons

---

**Version**: 2.0.0 (Multi-Role System)
**Status**: ✅ Production Ready
**Last Updated**: February 10, 2026

Made with ❤️ for the crypto community

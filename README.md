<<<<<<< HEAD
# CrypSync - Real-Time Cryptocurrency Tracker

A modern, scalable Flask-based web application for tracking cryptocurrency prices in real-time with multi-role access, portfolio management, advanced analytics, and comprehensive admin features.
=======
CrypSync - Cryptocurrency Real-Time Price Tracker
A modern, scalable cryptocurrency real-time price tracker built with Flask and AWS services. Features a sleek dark theme inspired by CoinStats with real-time data updates, interactive sparkline charts, and comprehensive market statistics.
>>>>>>> 64cba1722b5ad698c0cd61220a7f680daf62bf65

Features
Real-Time Price Tracking: Live cryptocurrency prices updated every 60 seconds from CoinGecko API

Market Statistics: Global market cap, 24h volume, and BTC dominance with live updates

Interactive Sparkline Charts: 7-day price trend visualizations using Canvas API

Favorites System: Save your favorite cryptocurrencies with localStorage persistence

<<<<<<< HEAD
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
=======
Advanced Search: Quickly find any cryptocurrency by name or symbol

Multi-Role System: Three distinct user experiences (User, Analyst, Admin)

Price Alerts: Set custom price thresholds with email notifications (requires login)

Historical Analysis: View price trends with interactive charts (requires login)

Portfolio Management: Track your crypto holdings with buy/sell transactions

Analyst Tools: Professional research dashboard with multi-coin comparison

User Authentication: Secure registration and login system with JWT tokens and bcrypt

Admin Panel: Comprehensive admin dashboard for user and coin management

Responsive Design: Modern dark UI that works seamlessly on desktop and mobile

AWS Integration: Production-ready deployment on AWS Elastic Beanstalk with DynamoDB

Tech Stack
Backend: Flask 2.3.3, Python 3.8+

Frontend: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3.0

Database: In-memory (development) / DynamoDB (production)

APIs: CoinGecko API v3 for cryptocurrency data

Authentication: JWT tokens with bcrypt password hashing (12 salt rounds)

Charts: Canvas API for sparklines, Chart.js 4.3.0 for detailed charts

Deployment: AWS Elastic Beanstalk, CloudWatch, SES

Quick Start
Prerequisites
Python 3.8 or higher

pip (Python package manager)

Installation
Clone the repository:

Bash
>>>>>>> 64cba1722b5ad698c0cd61220a7f680daf62bf65
git clone <repository-url>
cd crypsync
Create a virtual environment (recommended):

<<<<<<< HEAD
2. **Install dependencies**
```bash
=======
Bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

Bash
>>>>>>> 64cba1722b5ad698c0cd61220a7f680daf62bf65
pip install -r requirements.txt
Create a .env file (optional):

<<<<<<< HEAD
3. **Run the application**
```bash
=======
Bash
cp .env.example .env
Edit .env and add your configuration:

SECRET_KEY=your-secret-key-here
FLASK_ENV=development
COINGECKO_API_KEY=your-api-key-here (optional)
Running the Application
Start the Flask development server:

Bash
>>>>>>> 64cba1722b5ad698c0cd61220a7f680daf62bf65
python app.py
Open your browser and navigate to:

<<<<<<< HEAD
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
=======
http://localhost:5000
The home page displays real-time cryptocurrency prices with interactive charts and market statistics. No login required!

Usage Guide
Home Page (Public Access)
View Top Cryptocurrencies: See the top 50 coins by market cap

Real-Time Updates: Prices automatically refresh every 60 seconds

Sparkline Charts: Visual 7-day price trends for each cryptocurrency

Market Stats: Global market cap, 24h volume, and BTC dominance

Search: Find specific cryptocurrencies by name or symbol

Favorites: Click the star icon to save favorites (stored in browser)

Tabs: Switch between All Coins, Favorites, and Trending

Pagination: Navigate through pages to see more cryptocurrencies

Dashboard (Requires Login)
Monitor your favorite cryptocurrencies

View detailed price information

Access personalized data and settings

Alerts (Requires Login)
Create price alerts for specific cryptocurrencies

Set threshold values (above/below)

Get email notifications when prices reach your thresholds

Portfolio (Requires Login)
Track your cryptocurrency holdings

Buy and sell cryptocurrencies

View transaction history

Monitor profit/loss and portfolio value

Multi-Role System
CrypSync offers three distinct user experiences:

User Role - Portfolio & Trading

Personal portfolio management

Buy/sell cryptocurrencies

Transaction history

Price alerts and watchlist

Analyst Role - Research & Charts

Multi-coin comparison tools

Normalized price trend analysis

Volume comparison charts

Price correlation matrix

Custom date range selection

Professional research interface

Admin Role - System Management

User management dashboard

Coin tracking management

System health monitoring

Transaction monitoring across all users

Activity logs and alerts

Select your role at login to access the appropriate dashboard.

Admin Panel (Admin Only)
Access: Login with admin credentials (admin@crypsync.com / admin123)

User Management: View all users, delete users, monitor activity
>>>>>>> 64cba1722b5ad698c0cd61220a7f680daf62bf65

Coin Management: Add/remove tracked cryptocurrencies

<<<<<<< HEAD
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
=======
Statistics Dashboard: Monitor total users, transactions, and portfolio values

Transaction Monitoring: View all buy/sell transactions across the platform

Manage and delete existing alerts

Historical Data (Requires Login)
View historical price trends

Analyze price movements over custom date ranges

Generate detailed charts and reports

Project Structure
crypsync/
├── app.py                  # Main Flask application
├── services/               # Business logic services
│   ├── auth_service.py     # Authentication
│   ├── price_service.py    # Price fetching
│   ├── alert_service.py    # Alert management
│   ├── historical_service.py  # Historical data
│   └── visualization_service.py  # Chart data
├── templates/              # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── alerts.html
│   └── historical.html
├── static/                  # Static assets
│   ├── css/
│   │   └── style.css       # Custom styles
│   └── js/
│       ├── login.js
│       ├── register.js
│       ├── dashboard.js
│       ├── alerts.js
│       └── historical.js
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
API Endpoints
Public Endpoints
GET / - Home page with real-time crypto tracker

GET /home - Same as root, displays crypto tracker

Authentication
GET /register - Registration page

POST /register - Register new user

GET /login - Login page

POST /login - User login

GET /logout - User logout

Prices (Requires Authentication)
GET /api/prices?ids=bitcoin,ethereum - Get current cryptocurrency prices

Alerts (Requires Authentication)
GET /api/alerts - Get user's alerts

POST /api/alerts - Create new alert

DELETE /api/alerts?alert_id=<id> - Delete alert

Historical Data (Requires Authentication)
GET /api/historical?crypto_id=bitcoin&days=7 - Get historical price data

CoinGecko API Integration
The application uses the CoinGecko API v3 for real-time cryptocurrency data:

Rate Limits (Free Tier)
50 requests per minute

The application implements intelligent caching and rate limiting

Price data is cached for 60 seconds to minimize API calls

Circuit breaker pattern prevents API overload

Data Fetched
Current prices in USD

24-hour price changes

7-day price changes

Market capitalization

24-hour trading volume

7-day sparkline data (168 data points)

Global market statistics

Caching Strategy
Prices cached for 60 seconds

Automatic cache invalidation

Fallback to cached data if API is unavailable

Circuit breaker opens after 5 consecutive failures

Dark Theme Design
The application features a modern dark theme inspired by CoinStats:

Background: Deep black (#0a0a0a) for reduced eye strain

Cards: Dark gray (#1a1a1a) with subtle borders

Primary Color: Orange (#ff9500) for buttons and accents

Success: Green (#00d084) for positive price changes

Danger: Red (#ff4757) for negative price changes

Typography: System fonts for optimal readability

Animations: Smooth transitions and hover effects

Responsive: Mobile-first design with breakpoints

Development Notes
The application uses in-memory storage for development

For production, use AWS DynamoDB

CoinGecko API has rate limits - respect them to avoid blocking

Price data is cached to reduce API calls and improve performance

Favorites are stored in browser localStorage (no backend required)

JWT tokens expire after 24 hours

Passwords are hashed with bcrypt using 12 salt rounds

AWS Deployment
For production deployment on AWS Elastic Beanstalk with DynamoDB, CloudWatch, and SES:

Detailed AWS deployment includes:
>>>>>>> 64cba1722b5ad698c0cd61220a7f680daf62bf65

CloudFormation infrastructure setup

<<<<<<< HEAD
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Submit a pull request
=======
DynamoDB table configuration

IAM roles and policies

CloudWatch monitoring and alarms

SES email notifications

Automated deployment scripts

Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

Development Setup
Fork the repository
>>>>>>> 64cba1722b5ad698c0cd61220a7f680daf62bf65

Create a feature branch (git checkout -b feature/amazing-feature)

<<<<<<< HEAD
- Passwords hashed with bcrypt (12 salt rounds)
- JWT tokens with 24-hour expiration
- Session-based authentication
- Role-based access control
- SQL injection prevention
- XSS protection
- CSRF protection (recommended for production)
=======
Commit your changes (git commit -m 'Add amazing feature')

Push to the branch (git push origin feature/amazing-feature)

Open a Pull Request

Security
Passwords are hashed using bcrypt with 12 salt rounds

JWT tokens expire after 24 hours

Session tokens are validated on each authenticated request

HTTPS strongly recommended for production deployment

Environment variables for sensitive configuration

CORS protection enabled

SQL injection prevention (using parameterized queries)

Troubleshooting
API Rate Limit Errors
If you see "API_UNAVAILABLE" errors:

Wait 60 seconds for the rate limit to reset

The application will use cached data automatically
>>>>>>> 64cba1722b5ad698c0cd61220a7f680daf62bf65

Consider upgrading to CoinGecko Pro for higher limits

<<<<<<< HEAD
- API response caching
- Rate limiting (50 requests/minute)
- Database indexing
- Lazy loading
- Auto-refresh optimization
- Efficient queries
=======
Sparkline Charts Not Displaying
Ensure JavaScript is enabled in your browser

Check browser console for errors

Verify Canvas API is supported (all modern browsers)

Favorites Not Persisting
Favorites are stored in browser localStorage

Clearing browser data will remove favorites
>>>>>>> 64cba1722b5ad698c0cd61220a7f680daf62bf65

Use different browsers/devices = different favorites

<<<<<<< HEAD
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
=======
Performance
Initial page load: < 2 seconds

Price updates: Every 60 seconds

API response time: < 500ms (with caching)

Sparkline rendering: < 100ms per chart

Supports 1000+ concurrent users (with proper AWS scaling)

License
MIT License - see LICENSE file for details
>>>>>>> 64cba1722b5ad698c0cd61220a7f680daf62bf65

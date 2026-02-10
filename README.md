# CrypSync - Cryptocurrency Real-Time Price Tracker

A modern, scalable cryptocurrency real-time price tracker built with Flask and AWS services. Features a sleek dark theme inspired by CoinStats with real-time data updates, interactive sparkline charts, and comprehensive market statistics.

> 📚 **New to CrypSync?** Check out [INDEX.md](INDEX.md) for a complete documentation guide.

> 🚀 **Quick Start**: See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for setup guide.

> 🔐 **Admin Panel**: See [ADMIN_GUIDE.md](ADMIN_GUIDE.md) for admin documentation.

## Features

- **Real-Time Price Tracking**: Live cryptocurrency prices updated every 60 seconds from CoinGecko API
- **Market Statistics**: Global market cap, 24h volume, and BTC dominance with live updates
- **Interactive Sparkline Charts**: 7-day price trend visualizations using Canvas API
- **Favorites System**: Save your favorite cryptocurrencies with localStorage persistence
- **Advanced Search**: Quickly find any cryptocurrency by name or symbol
- **Multi-Role System**: Three distinct user experiences (User, Analyst, Admin)
- **Price Alerts**: Set custom price thresholds with email notifications (requires login)
- **Historical Analysis**: View price trends with interactive charts (requires login)
- **Portfolio Management**: Track your crypto holdings with buy/sell transactions
- **Analyst Tools**: Professional research dashboard with multi-coin comparison
- **User Authentication**: Secure registration and login system with JWT tokens and bcrypt
- **Admin Panel**: Comprehensive admin dashboard for user and coin management
- **Responsive Design**: Modern dark UI that works seamlessly on desktop and mobile
- **AWS Integration**: Production-ready deployment on AWS Elastic Beanstalk with DynamoDB

## Tech Stack

- **Backend**: Flask 2.3.3, Python 3.8+
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3.0
- **Database**: In-memory (development) / DynamoDB (production)
- **APIs**: CoinGecko API v3 for cryptocurrency data
- **Authentication**: JWT tokens with bcrypt password hashing (12 salt rounds)
- **Charts**: Canvas API for sparklines, Chart.js 4.3.0 for detailed charts
- **Deployment**: AWS Elastic Beanstalk, CloudWatch, SES

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd crypsync
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file (optional):
```bash
cp .env.example .env
```

Edit `.env` and add your configuration:
```
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
COINGECKO_API_KEY=your-api-key-here (optional)
```

### Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

The home page displays real-time cryptocurrency prices with interactive charts and market statistics. No login required!

## Usage Guide

### Home Page (Public Access)
- **View Top Cryptocurrencies**: See the top 50 coins by market cap
- **Real-Time Updates**: Prices automatically refresh every 60 seconds
- **Sparkline Charts**: Visual 7-day price trends for each cryptocurrency
- **Market Stats**: Global market cap, 24h volume, and BTC dominance
- **Search**: Find specific cryptocurrencies by name or symbol
- **Favorites**: Click the star icon to save favorites (stored in browser)
- **Tabs**: Switch between All Coins, Favorites, and Trending
- **Pagination**: Navigate through pages to see more cryptocurrencies

### Dashboard (Requires Login)
- Monitor your favorite cryptocurrencies
- View detailed price information
- Access personalized data and settings

### Alerts (Requires Login)
- Create price alerts for specific cryptocurrencies
- Set threshold values (above/below)
- Get email notifications when prices reach your thresholds

### Portfolio (Requires Login)
- Track your cryptocurrency holdings
- Buy and sell cryptocurrencies
- View transaction history
- Monitor profit/loss and portfolio value

### Multi-Role System
CrypSync offers three distinct user experiences:

**User Role** - Portfolio & Trading
- Personal portfolio management
- Buy/sell cryptocurrencies
- Transaction history
- Price alerts and watchlist

**Analyst Role** - Research & Charts
- Multi-coin comparison tools
- Normalized price trend analysis
- Volume comparison charts
- Price correlation matrix
- Custom date range selection
- Professional research interface

**Admin Role** - System Management
- User management dashboard
- Coin tracking management
- System health monitoring
- Transaction monitoring across all users
- Activity logs and alerts

Select your role at login to access the appropriate dashboard.

### Admin Panel (Admin Only)
- **Access**: Login with admin credentials (admin@crypsync.com / admin123)
- **User Management**: View all users, delete users, monitor activity
- **Coin Management**: Add/remove tracked cryptocurrencies
- **Statistics Dashboard**: Monitor total users, transactions, and portfolio values
- **Transaction Monitoring**: View all buy/sell transactions across the platform
- See [ADMIN_GUIDE.md](ADMIN_GUIDE.md) for detailed admin documentation
- Manage and delete existing alerts

### Historical Data (Requires Login)
- View historical price trends
- Analyze price movements over custom date ranges
- Generate detailed charts and reports

## Project Structure

```
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
├── static/                 # Static assets
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
```

## API Endpoints

### Public Endpoints
- `GET /` - Home page with real-time crypto tracker
- `GET /home` - Same as root, displays crypto tracker

### Authentication
- `GET /register` - Registration page
- `POST /register` - Register new user
- `GET /login` - Login page
- `POST /login` - User login
- `GET /logout` - User logout

### Prices (Requires Authentication)
- `GET /api/prices?ids=bitcoin,ethereum` - Get current cryptocurrency prices

### Alerts (Requires Authentication)
- `GET /api/alerts` - Get user's alerts
- `POST /api/alerts` - Create new alert
- `DELETE /api/alerts?alert_id=<id>` - Delete alert

### Historical Data (Requires Authentication)
- `GET /api/historical?crypto_id=bitcoin&days=7` - Get historical price data

## CoinGecko API Integration

The application uses the CoinGecko API v3 for real-time cryptocurrency data:

### Rate Limits (Free Tier)
- **50 requests per minute**
- The application implements intelligent caching and rate limiting
- Price data is cached for 60 seconds to minimize API calls
- Circuit breaker pattern prevents API overload

### Data Fetched
- Current prices in USD
- 24-hour price changes
- 7-day price changes
- Market capitalization
- 24-hour trading volume
- 7-day sparkline data (168 data points)
- Global market statistics

### Caching Strategy
- Prices cached for 60 seconds
- Automatic cache invalidation
- Fallback to cached data if API is unavailable
- Circuit breaker opens after 5 consecutive failures

## Dark Theme Design

The application features a modern dark theme inspired by CoinStats:

- **Background**: Deep black (#0a0a0a) for reduced eye strain
- **Cards**: Dark gray (#1a1a1a) with subtle borders
- **Primary Color**: Orange (#ff9500) for buttons and accents
- **Success**: Green (#00d084) for positive price changes
- **Danger**: Red (#ff4757) for negative price changes
- **Typography**: System fonts for optimal readability
- **Animations**: Smooth transitions and hover effects
- **Responsive**: Mobile-first design with breakpoints

## Development Notes

- The application uses in-memory storage for development
- For production, use AWS DynamoDB (see AWS deployment section)
- CoinGecko API has rate limits - respect them to avoid blocking
- Price data is cached to reduce API calls and improve performance
- Favorites are stored in browser localStorage (no backend required)
- JWT tokens expire after 24 hours
- Passwords are hashed with bcrypt using 12 salt rounds

## AWS Deployment

For production deployment on AWS Elastic Beanstalk with DynamoDB, CloudWatch, and SES:

See [README_AWS.md](README_AWS.md) for detailed AWS deployment instructions including:
- CloudFormation infrastructure setup
- DynamoDB table configuration
- IAM roles and policies
- CloudWatch monitoring and alarms
- SES email notifications
- Automated deployment scripts

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security

- Passwords are hashed using bcrypt with 12 salt rounds
- JWT tokens expire after 24 hours
- Session tokens are validated on each authenticated request
- HTTPS strongly recommended for production deployment
- Environment variables for sensitive configuration
- CORS protection enabled
- SQL injection prevention (using parameterized queries)

## Troubleshooting

### API Rate Limit Errors
If you see "API_UNAVAILABLE" errors:
- Wait 60 seconds for the rate limit to reset
- The application will use cached data automatically
- Consider upgrading to CoinGecko Pro for higher limits

### Sparkline Charts Not Displaying
- Ensure JavaScript is enabled in your browser
- Check browser console for errors
- Verify Canvas API is supported (all modern browsers)

### Favorites Not Persisting
- Favorites are stored in browser localStorage
- Clearing browser data will remove favorites
- Use different browsers/devices = different favorites

## Performance

- Initial page load: < 2 seconds
- Price updates: Every 60 seconds
- API response time: < 500ms (with caching)
- Sparkline rendering: < 100ms per chart
- Supports 1000+ concurrent users (with proper AWS scaling)

## Browser Support

- Chrome 90+ ✅
- Firefox 88+ ✅
- Safari 14+ ✅
- Edge 90+ ✅
- Mobile browsers ✅

## Acknowledgments

- [CoinGecko API](https://www.coingecko.com/en/api) - Cryptocurrency data provider
- [CoinStats](https://coinstats.app/) - Design inspiration for dark theme
- [Flask](https://flask.palletsprojects.com/) - Python web framework
- [Bootstrap](https://getbootstrap.com/) - UI component library
- [Chart.js](https://www.chartjs.org/) - Charting library
- [Font Awesome](https://fontawesome.com/) - Icon library

## License

MIT License - see LICENSE file for details




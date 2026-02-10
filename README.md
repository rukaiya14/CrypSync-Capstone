# CrypSync - Real-Time Cryptocurrency Tracker

A Flask-based web application for tracking cryptocurrency prices in real-time with user authentication, portfolio management, price alerts, and admin management features.

## Features

### Core Functionality

**Real-Time Price Tracking**: Live updates for Bitcoin, Ethereum, Solana, and more

**User Authentication**: Secure login/signup system with JWT tokens and bcrypt password hashing

**Multi-Role Access**: Three user roles (User, Analyst, Admin) with distinct dashboards

**Portfolio Management**: Track cryptocurrency holdings with buy/sell transactions

**Price Alerts**: Set custom price thresholds with visual and browser notifications

**Historical Charts**: View price history with 7, 30, 90, 180, and 365-day views

**Live Search**: Filter and search through tracked cryptocurrencies

**Admin Panel**: Manage tracked coins, view user statistics, and monitor system health

### User Interface

- Clean, responsive design using Bootstrap 5
- Real-time price updates without page refresh
- Interactive price alert system
- Mobile-friendly responsive layout

## Technology Stack

### Backend
- **Python Flask** - Web framework
- **JWT & bcrypt** - Secure authentication
- **SQLite** - Database storage
- **Requests** - API calls to CoinGecko

### Frontend
- **HTML5 & CSS3**
- **Bootstrap 5** - UI framework
- **JavaScript** - Dynamic interactions
- **Chart.js** - Data visualization

### Data Source
- **CoinGecko API** - Real-time cryptocurrency data

## Installation & Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd CrypSync
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
- Open your browser and go to **http://localhost:5000**
- Use demo credentials: `admin@crypsync.com` / `admin123` for admin access
- Or create a new user account

## Project Structure

```
CrypSync/
 app.py                 # Main Flask application
 database.py            # Database management
 requirements.txt       # Python dependencies
 README.md             # Project documentation
 services/             # Business logic
    auth_service.py
    price_service.py
    alert_service.py
    portfolio_service_db.py
    admin_service.py
    system_service.py
 templates/            # HTML templates
    base.html         # Base template
    login.html        # Login page
    register.html     # Registration page
    home.html         # Homepage
    dashboard.html    # User dashboard
    analyst_dashboard.html  # Analyst dashboard
    admin_dashboard.html    # Admin panel
    portfolio.html    # Portfolio page
    about.html        # About page
 static/               # Static assets
     css/
        style.css     # Custom styles
     js/
         *.js          # JavaScript functionality
```

## Usage

### For Regular Users

1. Sign up for a new account or use existing credentials
2. Select **"User"** role at login
3. View Dashboard to see live cryptocurrency prices
4. Add Holdings via Portfolio page to track investments
5. Set Price Alerts by clicking "Set Alert" next to any coin
6. Search Coins using the search bar to filter results
7. Monitor Alerts - get visual and browser notifications when price thresholds are met

### For Analysts

1. Login and select **"Analyst"** role
2. Access Analyst Dashboard for research tools
3. Compare multiple cryptocurrencies with normalized charts
4. Analyze price correlations
5. View historical data with custom date ranges

### For Administrators

1. Login with admin credentials (`admin@crypsync.com` / `admin123`)
2. Select **"Admin"** role at login
3. Access Admin Panel from the navigation menu
4. Add/Remove Coins to customize which cryptocurrencies are tracked
5. View User Statistics to see registered users and system usage
6. Monitor system health and API status

## API Endpoints

- `GET /` - Dashboard (requires authentication)
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /register` - Registration page
- `POST /register` - Process registration
- `GET /admin` - Admin panel (admin only)
- `GET /analyst` - Analyst dashboard
- `GET /about` - About page
- `GET /api/prices` - JSON API for current prices
- `GET /api/portfolio` - Get user portfolio
- `POST /api/portfolio/buy` - Buy cryptocurrency
- `POST /api/portfolio/sell` - Sell cryptocurrency
- `GET /api/historical` - Get historical price data
- `POST /api/alerts` - Create price alert
- `POST /api/admin/coins/add` - Add coin to tracking (admin only)
- `POST /api/admin/coins/remove` - Remove coin from tracking (admin only)

## Features in Detail

### Real-Time Price Updates
- Automatic refresh every 60 seconds
- Manual refresh button available
- Color-coded 24-hour change indicators
- Responsive price formatting

### Price Alert System
- Set alerts above or below current price
- Visual notifications with color-coded table rows
- Browser notifications (with user permission)
- Persistent alerts stored in database

### Portfolio Management
- Add cryptocurrency holdings manually
- Track purchase price and current value
- Real-time profit/loss calculation
- Transaction history
- Buy/sell functionality

### User Management
- Secure password hashing with bcrypt
- JWT token-based authentication
- Role-based access control (user/analyst/admin)
- SQLite database storage

### Admin Features
- Add/remove tracked cryptocurrencies
- View all registered users
- Real-time coin management
- User statistics dashboard
- System health monitoring
- Transaction monitoring

### Multi-Role System
- **User Dashboard**: Portfolio and trading focus
- **Analyst Dashboard**: Research and comparison tools
- **Admin Dashboard**: System management console

## Demo Credentials

- **Admin Access**: Email: `admin@crypsync.com`, Password: `admin123`
- **Regular User**: Create new account via signup page

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
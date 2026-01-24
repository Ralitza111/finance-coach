"""
Create Finance Knowledge Base

Builds a FAISS vector database with comprehensive financial knowledge including:
- Financial concepts (stocks, bonds, ETFs, mutual funds, etc.)
- Investment strategies and portfolio management
- Tax concepts and regulations
- Market analysis and indicators
- Financial planning and goal setting
"""

import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

load_dotenv()

# Initialize embeddings
embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

# ==================== KNOWLEDGE BASE CONTENT ====================

# Financial Concepts
financial_concepts = [
    """
    **Stock** is a type of security that represents ownership in a corporation.
    - Stock owners (shareholders) are entitled to a portion of the company's assets and earnings
    - Two main types: Common stock (voting rights) and Preferred stock (priority dividends)
    - Traded on stock exchanges like NYSE, NASDAQ
    - Price determined by supply and demand, company performance, market conditions
    - Capital gains occur when stock price increases; dividends provide regular income
    - Risk: Stock prices can be volatile and may lose value
    """,
    
    """
    **Bond** is a fixed-income investment representing a loan made by an investor to a borrower.
    - Issuer (borrower) pays periodic interest (coupon) and returns principal at maturity
    - Types: Government bonds (Treasury), Corporate bonds, Municipal bonds
    - Generally lower risk than stocks but lower potential returns
    - Bond prices inversely related to interest rates
    - Credit rating affects bond yield and risk (AAA is highest quality)
    - Used for income generation and portfolio diversification
    """,
    
    """
    **ETF (Exchange-Traded Fund)** is a basket of securities that trades on an exchange like a stock.
    - Offers diversification by holding multiple stocks, bonds, or other assets
    - Lower fees than mutual funds (typically 0.03% - 0.25%)
    - Can be bought/sold throughout trading day at market price
    - Popular types: S&P 500 ETFs (SPY, VOO), Bond ETFs, Sector ETFs
    - Tax-efficient due to creation/redemption mechanism
    - Examples: VOO (Vanguard S&P 500), QQQ (Nasdaq 100), AGG (Bond Aggregate)
    """,
    
    """
    **Mutual Fund** is a pooled investment vehicle managed by professional fund managers.
    - Investors buy shares of the fund, which invests in diversified portfolio
    - Priced once per day after market close (NAV - Net Asset Value)
    - Higher fees than ETFs (expense ratios typically 0.5% - 2%)
    - Active management (managers pick stocks) or passive (index funds)
    - Minimum investment requirements (often $1,000 - $3,000)
    - Examples: Vanguard 500 Index Fund, Fidelity Contrafund
    """,
    
    """
    **Diversification** is the practice of spreading investments across different assets to reduce risk.
    - "Don't put all eggs in one basket" - reduces exposure to any single investment
    - Diversify across asset classes (stocks, bonds, real estate, commodities)
    - Diversify within asset classes (different sectors, company sizes, countries)
    - Modern Portfolio Theory: Optimal diversification improves risk-adjusted returns
    - Reduces unsystematic risk (company-specific) but not systematic risk (market-wide)
    - Recommended: 60/40 stock/bond allocation for moderate risk, adjust based on age
    """,
    
    """
    **Asset Allocation** is the strategy of dividing investment portfolio among different asset categories.
    - Primary asset classes: Stocks (equities), Bonds (fixed income), Cash, Real estate
    - Determines 90% of portfolio performance variation over time
    - Age-based rule: Stock allocation = 110 - your age (e.g., age 30 → 80% stocks)
    - Aggressive: 80-100% stocks, Moderate: 60% stocks/40% bonds, Conservative: 40% stocks/60% bonds
    - Rebalance annually to maintain target allocation
    - Adjust based on risk tolerance, time horizon, financial goals
    """,
    
    """
    **Dollar-Cost Averaging (DCA)** is investing fixed amounts at regular intervals regardless of price.
    - Reduces impact of market volatility and timing risk
    - Example: Invest $500 monthly instead of $6,000 lump sum
    - Buys more shares when prices low, fewer when prices high
    - Psychologically easier than trying to time the market
    - Ideal for 401(k) contributions and regular investing
    - May underperform lump-sum investing in rising markets
    """,
    
    """
    **Index Fund** is a mutual fund or ETF designed to track a specific market index.
    - Passive management: Simply matches index holdings, no active stock picking
    - Very low fees (often 0.03% - 0.20%)
    - Examples: S&P 500 index funds, Total Stock Market index funds
    - Consistently outperforms most actively managed funds over long term
    - Warren Buffett recommends index funds for most investors
    - Popular: Vanguard Total Stock Market (VTI), S&P 500 (VOO, SPY)
    """,
    
    """
    **401(k)** is an employer-sponsored retirement savings plan with tax advantages.
    - Contributions reduce taxable income (traditional) or grow tax-free (Roth)
    - 2024 contribution limit: $23,000 ($30,500 if age 50+)
    - Many employers offer matching contributions (free money!)
    - Withdrawal penalty if taken before age 59½ (10% + taxes)
    - Required Minimum Distributions (RMDs) start at age 73
    - Always contribute enough to get full employer match
    """,
    
    """
    **IRA (Individual Retirement Account)** is a tax-advantaged retirement account.
    - Traditional IRA: Tax-deductible contributions, taxed upon withdrawal
    - Roth IRA: After-tax contributions, tax-free qualified withdrawals
    - 2024 contribution limit: $7,000 ($8,000 if age 50+)
    - Roth IRA income limits: $161,000 single, $240,000 married (2024)
    - Withdrawals before 59½ may incur penalties
    - Roth IRA has no RMDs during owner's lifetime
    """,
    
    """
    **Compound Interest** is earning interest on both principal and accumulated interest.
    - "The most powerful force in the universe" - Einstein (allegedly)
    - Formula: A = P(1 + r/n)^(nt) where P=principal, r=rate, n=compounds/year, t=years
    - Example: $10,000 at 8% for 30 years = $100,627
    - Time is crucial: Starting 10 years earlier can double retirement savings
    - Applies to investments, savings, and debt (credit cards compound against you)
    - Key to long-term wealth building
    """,
    
    """
    **Expense Ratio** is the annual fee charged by mutual funds and ETFs.
    - Expressed as percentage of assets (e.g., 0.10% = $10 per $10,000 invested)
    - Directly reduces investment returns every year
    - 1% difference in fees can cost hundreds of thousands over lifetime
    - Index funds: 0.03% - 0.20%, Active funds: 0.50% - 2.00%
    - Lower is better - every 0.10% matters over decades
    - Total market ETFs often have lowest ratios (0.03% - 0.04%)
    """,
    
    """
    **Capital Gains** is profit from selling an asset for more than purchase price.
    - Short-term: Held ≤1 year, taxed as ordinary income (10%-37%)
    - Long-term: Held >1 year, preferential tax rates (0%, 15%, or 20%)
    - 2024 long-term rates: 0% up to $44k single/$89k married, 15% up to $492k/$553k, 20% above
    - Capital losses can offset gains (tax-loss harvesting strategy)
    - $3,000 annual limit for deducting losses against ordinary income
    - Hold investments >1 year when possible for tax efficiency
    """,
    
    """
    **Dividend** is a portion of company profits paid to shareholders.
    - Paid quarterly by many large, established companies
    - Dividend Yield = Annual dividend / Stock price (e.g., 3% yield)
    - Qualified dividends taxed at capital gains rates (0%, 15%, 20%)
    - Dividend aristocrats: Companies increasing dividends 25+ consecutive years
    - Dividend stocks provide income but may have lower growth
    - Examples: Coca-Cola, Johnson & Johnson, Procter & Gamble
    """,
    
    """
    **P/E Ratio (Price-to-Earnings)** measures stock valuation relative to earnings.
    - Formula: Stock Price / Earnings Per Share
    - S&P 500 historical average: ~16-17
    - High P/E (>25): Stock may be overvalued or high-growth expectations
    - Low P/E (<15): Stock may be undervalued or facing challenges
    - Compare P/E to industry peers and company's historical average
    - Limitations: Doesn't account for growth, debt, or industry differences
    """,
    
    """
    **Market Capitalization** is total value of company's outstanding shares.
    - Formula: Current Stock Price × Total Shares Outstanding
    - Large-cap: >$10B (Microsoft, Apple), more stable, lower growth
    - Mid-cap: $2B-$10B, balance of growth and stability
    - Small-cap: $300M-$2B, higher growth potential, higher volatility
    - Micro-cap: <$300M, very high risk
    - Diversify across market caps for balanced portfolio
    - S&P 500 contains large-cap stocks
    """,
    
    """
    **Bull Market** is a period of rising stock prices and investor optimism.
    - Typically defined as 20%+ increase from recent low
    - Characterized by strong economy, low unemployment, investor confidence
    - Average bull market lasts 4-5 years (historically)
    - Strategy: Stay invested, maintain discipline, avoid overconfidence
    - Don't try to predict the top - remain diversified
    - Historic examples: 2009-2020 (longest bull market)
    """,
    
    """
    **Bear Market** is a period of falling stock prices and pessimism.
    - Typically defined as 20%+ decline from recent high
    - Caused by recession, high inflation, economic crisis, pandemic
    - Average bear market lasts 9-18 months
    - Strategy: Don't panic sell, continue investing (stocks on sale)
    - Historically, markets always recover and reach new highs
    - Historic examples: 2008 financial crisis, 2020 COVID crash
    """,
    
    """
    **Recession** is a significant decline in economic activity lasting several months.
    - Technical definition: Two consecutive quarters of negative GDP growth
    - Indicators: Rising unemployment, declining consumer spending, business closures
    - Average recession lasts 10-18 months
    - Stock market often declines before recession begins (leading indicator)
    - Investment strategy: Maintain course, consider defensive stocks, bonds
    - Historically occurs every 5-10 years
    """,
    
    """
    **Inflation** is the rate at which general prices for goods and services rise.
    - Measured by CPI (Consumer Price Index) and PCE (Personal Consumption Expenditures)
    - Federal Reserve targets 2% annual inflation
    - High inflation (>4%) erodes purchasing power and savings
    - Deflation (negative inflation) can harm economy
    - Stocks and real estate historically outpace inflation long-term
    - TIPS (Treasury Inflation-Protected Securities) adjust for inflation
    """,
    
    """
    **Federal Reserve (The Fed)** is the central banking system of the United States.
    - Sets monetary policy to promote maximum employment and price stability
    - Primary tool: Federal Funds Rate (interest rate for bank lending)
    - Raising rates: Slows economy, fights inflation, may lower stock prices
    - Lowering rates: Stimulates economy, may boost stocks, increases inflation risk
    - FOMC (Federal Open Market Committee) meets 8 times per year
    - Fed decisions significantly impact all financial markets
    """,
    
    """
    **Interest Rate** is the cost of borrowing money or return on savings/bonds.
    - Set by Federal Reserve (Fed Funds Rate) influences all other rates
    - Higher rates: Savings accounts pay more, bonds attractive, stocks may fall
    - Lower rates: Cheaper borrowing, stocks more attractive, savings earn less
    - Mortgage rates, auto loans, credit cards all follow Fed rate direction
    - Bond prices inversely related to rates (rates ↑, bond prices ↓)
    - Affects your investment returns, loan costs, retirement planning
    """,
    
    """
    **Risk Tolerance** is your ability and willingness to endure investment losses.
    - Factors: Age, income, financial goals, personality, investment timeline
    - High risk tolerance: Can handle volatility, longer time horizon (20+ years)
    - Low risk tolerance: Prefer stability, shorter timeline, near retirement
    - Questionnaire helps determine: conservative, moderate, or aggressive
    - Risk capacity (financial ability) may differ from risk appetite (emotional comfort)
    - Match portfolio allocation to risk tolerance (aggressive = more stocks)
    """,
    
    """
    **Emergency Fund** is savings reserved for unexpected expenses or income loss.
    - Recommended: 3-6 months of living expenses
    - Keep in high-yield savings account (HYSA) - currently 4-5% APY
    - Must be liquid (easily accessible) - not invested in stocks
    - First financial priority before investing
    - Prevents needing to sell investments at wrong time or use high-interest debt
    - Examples: Job loss, medical emergency, car/home repairs
    """,
    
    """
    **Rebalancing** is adjusting portfolio back to target asset allocation.
    - Example: 60/40 stocks/bonds becomes 70/30 after stocks rise → sell stocks, buy bonds
    - Enforces "buy low, sell high" discipline
    - Recommended frequency: Annually or when allocation drifts 5%+
    - Methods: Sell winners/buy losers, or direct new contributions to lagging assets
    - In tax-advantaged accounts (401k, IRA) to avoid capital gains taxes
    - Maintains desired risk level and prevents overexposure
    """,
    
    """
    **Tax-Loss Harvesting** is selling investments at a loss to offset capital gains.
    - Reduces tax burden by offsetting gains with losses
    - Can deduct up to $3,000 in net losses against ordinary income annually
    - Excess losses carry forward to future years indefinitely
    - Wash sale rule: Can't buy "substantially identical" security within 30 days
    - Best done in taxable brokerage accounts (not IRAs/401ks)
    - Automated by robo-advisors like Betterment, Wealthfront
    """,
    
    """
    **Roth Conversion** is transferring money from traditional IRA to Roth IRA.
    - Pay taxes now on converted amount at current tax rate
    - Future withdrawals completely tax-free (qualified distributions)
    - Strategic during low-income years or when tax rates low
    - No income limits for conversions (unlike Roth IRA contributions)
    - Consider tax bracket impact - may push into higher bracket
    - Five-year rule: Each conversion has 5-year clock for penalty-free withdrawal
    """,
    
    """
    **HSA (Health Savings Account)** is a triple-tax-advantaged medical savings account.
    - Requires high-deductible health plan (HDHP)
    - 2024 limits: $4,150 individual, $8,300 family (+$1,000 if 55+)
    - Triple tax benefit: Tax-deductible contributions, tax-free growth, tax-free medical withdrawals
    - Can invest HSA funds in stocks/bonds like IRA
    - No "use it or lose it" - funds roll over indefinitely
    - After 65, can withdraw for non-medical (taxed like traditional IRA)
    """,
    
    """
    **Backdoor Roth IRA** is a strategy for high-income earners to contribute to Roth IRA.
    - Step 1: Contribute to traditional IRA (non-deductible)
    - Step 2: Immediately convert to Roth IRA
    - Bypasses Roth IRA income limits ($161k single, $240k married in 2024)
    - Pro-rata rule: If you have pre-tax IRA money, conversion partially taxable
    - Requires careful execution and tax reporting
    - Legal strategy explicitly allowed by IRS
    """,
    
    """
    **Mega Backdoor Roth** is advanced strategy to contribute large amounts to Roth accounts.
    - Use after-tax 401(k) contributions beyond normal $23,000 limit
    - Total 401(k) limit: $69,000 in 2024 (including employer match)
    - Convert after-tax contributions to Roth 401(k) or Roth IRA
    - Not all 401(k) plans allow this - check plan rules
    - Can contribute $46,000+ additional to Roth annually if available
    - Complex but powerful for high earners with access
    """,
]

# Investment Strategies
investment_strategies = [
    """
    **Buy and Hold Strategy** is investing for long term without frequent trading.
    - Core principle: Time in market beats timing the market
    - Reduces transaction costs, taxes, and emotional decisions
    - Ignore short-term volatility and market noise
    - S&P 500 historical return: ~10% annually over long periods
    - Best for index fund investors and retirement accounts
    - Warren Buffett's favorite strategy
    """,
    
    """
    **Three-Fund Portfolio** is a simple diversification strategy using just 3 index funds.
    - Fund 1: Total US Stock Market (e.g., VTI, VTSAX) - 60%
    - Fund 2: Total International Stock (e.g., VXUS, VTIAX) - 30%
    - Fund 3: Total Bond Market (e.g., BND, VBTLX) - 10%
    - Adjust percentages based on age and risk tolerance
    - Extremely low cost, simple to manage, well-diversified
    - Popularized by Bogleheads investment philosophy
    """,
    
    """
    **Target-Date Fund** is an all-in-one fund that adjusts allocation as target date approaches.
    - Automatically becomes more conservative over time (glide path)
    - Example: 2060 Target Date fund (for ~2060 retirement)
    - Young: 90% stocks, 10% bonds → Near retirement: 30% stocks, 70% bonds
    - Extremely simple - one fund for entire retirement
    - Slightly higher fees than DIY three-fund portfolio (0.12% vs 0.04%)
    - Popular in 401(k) plans - good "set and forget" option
    """,
    
    """
    **Value Investing** is buying undervalued stocks trading below intrinsic value.
    - Focus on low P/E ratios, high dividend yields, strong fundamentals
    - Philosophy: Market overreacts, creating opportunities
    - Famous practitioners: Warren Buffett, Benjamin Graham
    - Look for strong balance sheets, consistent earnings, competitive advantages
    - Requires patience - may underperform during growth stock rallies
    - Value stocks historically outperform long-term but more cyclical
    """,
    
    """
    **Growth Investing** is buying companies expected to grow faster than market average.
    - Characteristics: High P/E ratios, revenue growth, innovation
    - Often tech companies (historically): Amazon, Apple, Google, Tesla
    - Higher risk and volatility than value stocks
    - May not pay dividends (reinvest profits for growth)
    - Can outperform dramatically in bull markets
    - More sensitive to interest rate changes
    """,
    
    """
    **4% Rule** is retirement withdrawal strategy to make savings last 30 years.
    - Withdraw 4% of portfolio in first year of retirement
    - Adjust subsequent withdrawals for inflation
    - Example: $1M portfolio → $40,000 first year withdrawal
    - Based on historical success rates (95% success over 30 years)
    - More conservative: 3-3.5% rule for longer retirements
    - Adjust based on market conditions and spending needs
    """,
]

# Tax Concepts
tax_concepts = [
    """
    **Standard Deduction** is the fixed amount reducing taxable income without itemizing.
    - 2024: $14,600 single, $29,200 married filing jointly
    - Most taxpayers use standard deduction (simpler)
    - Itemize only if deductions exceed standard deduction
    - Common itemized deductions: Mortgage interest, state taxes (SALT), charitable donations
    - Standard deduction indexed to inflation annually
    - Simplifies tax filing for most Americans
    """,
    
    """
    **Tax Brackets** are ranges of income taxed at increasing rates (progressive taxation).
    - 2024 Federal brackets: 10%, 12%, 22%, 24%, 32%, 35%, 37%
    - Only income within bracket taxed at that rate (marginal tax rate)
    - Example: Single filer earning $50k pays 10% on first $11k, 12% on $11k-$47k, 22% on rest
    - Moving into higher bracket doesn't increase tax on lower income
    - Effective tax rate (average) always lower than marginal rate
    - Long-term capital gains have separate preferential brackets
    """,
    
    """
    **Tax-Advantaged Accounts** are investment accounts with special tax benefits.
    - Traditional 401(k)/IRA: Tax deduction now, taxed later
    - Roth 401(k)/IRA: Taxed now, tax-free forever
    - HSA: Triple tax advantage (deductible, grows tax-free, withdrawals tax-free for medical)
    - 529: Tax-free growth and withdrawals for education
    - Priority: Max 401(k) match > IRA/Roth IRA > Max 401(k) > HSA > Taxable brokerage
    - Massive long-term tax savings through compound growth
    """,
    
    """
    **FICA Taxes** are payroll taxes funding Social Security and Medicare.
    - Social Security: 6.2% employee + 6.2% employer (12.4% total)
    - Medicare: 1.45% employee + 1.45% employer (2.9% total)
    - 2024 Social Security wage cap: $168,600 (Medicare uncapped)
    - Additional 0.9% Medicare tax on high earners ($200k+ single, $250k+ married)
    - Self-employed pay full 15.3% but get deduction for half
    - Separate from income tax - automatically withheld from paychecks
    """,
]

# Market Indicators
market_indicators = [
    """
    **S&P 500** is stock market index tracking 500 largest US companies.
    - Represents ~80% of total US stock market value
    - Market-cap weighted (larger companies have more influence)
    - Top holdings: Apple, Microsoft, Amazon, Google, NVIDIA
    - Considered best gauge of overall US stock market health
    - Historical return: ~10% annually including dividends
    - Popular investment vehicles: SPY, VOO, IVV index funds
    """,
    
    """
    **Dow Jones Industrial Average (DJIA)** tracks 30 large US blue-chip companies.
    - Price-weighted (higher stock price = more influence, unusual)
    - Oldest US market index (created 1896)
    - Less representative than S&P 500 (only 30 stocks)
    - Includes: Apple, Microsoft, Boeing, Disney, Goldman Sachs
    - Frequently cited in media but less useful for investors
    - Popular ETF: DIA
    """,
    
    """
    **NASDAQ Composite** is index of all stocks listed on NASDAQ exchange.
    - Heavy technology concentration (~50% tech stocks)
    - Includes: Apple, Microsoft, Amazon, Google, Tesla, Meta
    - More volatile than S&P 500 due to growth stock concentration
    - Strong indicator of technology sector performance
    - Popular tech-focused ETF: QQQ (Nasdaq-100)
    - Higher growth potential but higher risk
    """,
    
    """
    **VIX (Volatility Index)** measures expected stock market volatility.
    - Called "fear gauge" or "fear index"
    - Based on S&P 500 options prices (30-day forward looking)
    - Normal: 12-20, Elevated: 20-30, High: 30+, Extreme: 40+
    - Typically spikes during market crashes and uncertainly
    - 2020 COVID: VIX hit 80+, 2008 crisis: 80+
    - Inverse correlation with stocks (VIX up = stocks down usually)
    """,
    
    """
    **Treasury Yield Curve** plots yields of US Treasury bonds across maturities.
    - Normal curve: Long-term yields higher than short-term (upward sloping)
    - Inverted curve: Short-term yields exceed long-term (downward sloping)
    - Inverted curve predicts recession within 6-24 months (historically accurate)
    - 2s/10s spread most watched (2-year vs 10-year Treasury)
    - Reflects investor expectations for interest rates and economy
    - Fed controls short end, market controls long end
    """,
]

# Financial Planning
financial_planning = [
    """
    **FIRE (Financial Independence, Retire Early)** is movement to achieve financial independence through aggressive saving.
    - Save 50-70% of income, invest in low-cost index funds
    - Target: 25x annual expenses invested (4% rule)
    - Example: Need $40k/year → Save $1M → Retire early
    - Variations: Lean FIRE (<$40k/year), Fat FIRE ($100k+/year), Barista FIRE (part-time work)
    - Requires high income, low expenses, aggressive investing
    - Typical timeline: 10-20 years depending on savings rate
    """,
    
    """
    **Net Worth** is total assets minus total liabilities.
    - Assets: Cash, investments, home equity, retirement accounts
    - Liabilities: Mortgage, student loans, credit cards, car loans
    - Formula: Net Worth = Assets - Liabilities
    - Track quarterly or annually to measure financial progress
    - Average US net worth: $192k (median: $121k) 
    - Focus on increasing assets and decreasing liabilities over time
    """,
    
    """
    **Debt Avalanche** is debt repayment strategy targeting highest interest rate first.
    - Pay minimums on all debts, extra to highest interest rate debt
    - Mathematically optimal - saves most on interest
    - Example: Pay off 20% credit card before 6% car loan before 4% student loan
    - Slower psychological wins than debt snowball method
    - Best for financially disciplined individuals
    - Can save thousands in interest over time
    """,
    
    """
    **Debt Snowball** is debt repayment strategy targeting smallest balance first.
    - Pay minimums on all debts, extra to smallest balance
    - Quick psychological wins motivate continued progress
    - Example: Pay off $500 credit card before $5,000 car loan before $30,000 student loan
    - May cost more in interest than avalanche method
    - Popularized by Dave Ramsey
    - Better for those needing motivation and quick wins
    """,
    
    """
    **Credit Score** is numerical representation of creditworthiness (300-850).
    - Factors: Payment history (35%), amounts owed (30%), length of history (15%), new credit (10%), types (10%)
    - Excellent: 750+, Good: 700-749, Fair: 650-699, Poor: <650
    - Affects: Loan approval, interest rates, insurance premiums, apartment rentals
    - Improve by: Pay on time, keep utilization <30%, don't close old cards, limit new applications
    - Check free annually: AnnualCreditReport.com (official site)
    - Takes time to build - length of history matters
    """,
]

# Combine all content
all_documents = (
    financial_concepts + 
    investment_strategies + 
    tax_concepts + 
    market_indicators + 
    financial_planning
)

# Create Document objects
documents = [
    Document(page_content=content.strip(), metadata={"source": "finance_knowledge"})
    for content in all_documents
]

print(f"📚 Creating knowledge base with {len(documents)} documents...")

# Create FAISS vector store
db = FAISS.from_documents(documents, embeddings)

# Save to disk
output_path = "./knowledge_base/faiss_index"
os.makedirs(output_path, exist_ok=True)
db.save_local(output_path)

print(f"✅ Knowledge base created successfully!")
print(f"📁 Saved to: {output_path}")
print(f"📊 Total documents: {len(documents)}")
print(f"💾 Vector database ready for use!")

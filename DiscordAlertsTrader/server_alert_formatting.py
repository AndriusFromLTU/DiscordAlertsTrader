import re
from datetime import datetime, timedelta


def server_formatting(message):
    """Format server messages to standard alert format"""
    if message.guild is None:  # DM
        return message
    if message.guild.id == 542224582317441034:
        message = xtrades_formatting(message)
    elif message.guild.id in [836435995854897193, 1208184842441719828]:
        message = tradeproelite_formatting(message)
    elif message.channel.id in [
        1235324287703973998,
        1235324289222443008,
        1235324286437163129,
    ]:
        message = prosperitytrades_formatting(message)
    elif message.channel.id in [
        1144658745822035978,
        1196385162490032128,
        1176558956123013230,
        1213995695237763145,
        1224336566907044032,
        1167905511711178953,
    ]:
        message = eclipse_alerts(message)
    elif message.channel.id in [
        1005221780941709312,
        1176559103431168001,
        1222679083155193867,
    ]:
        message = oculus_alerts(message)
    elif message.channel.id in [989674163331534929]:
        message = rough_alerts(message)
    elif message.channel.id in [1221951275998908527]:
        message = clutch_trades(message)
    elif message.channel.id in [972620961004269598]:
        message = kent_formatting(message)
    elif message.channel.id in [
        894421928968871986,
        1184315998980022342,
        1186220832226283560,
        1184315998980022342,
    ]:
        message = sirgoldman_formatting(message)
    elif message.channel.id in [
        1090673126527996004,
        1132799545491869857,
        1106356727294726156,
        1135628574511079505,
        1184315961726226502,
        1184286853734600704,
        1225021701281021994,
    ]:
        message = flint_formatting(message)
    elif message.channel.id in [
        904543469266161674,
        1209644125477933088,
        1221952610987147284,
    ]:
        message = jpm_formatting(message)
    elif message.channel.id in [
        911389167169191946,
        1158799914290139188,
        1221952209542053949,
    ]:
        message = nitro_formatting(message)
    elif message.channel.id in [
        1189288104545226773,
        1012144319282556928,
        1214378575554150440,
    ]:
        message = moneymotive(message)
    elif message.channel.id in [728711121128652851]:
        message = owl_formatting(message)
    elif message.channel.id in [979906463487103006, 1247896425585704992]:
        message = bear_alerts(message)
    elif message.channel.id in [1107395495460081754, 1209855407636488212]:
        message = diesel_formatting(message)
    elif message.channel.id in [
        1204586438679863326,
        1204586623015067698,
        1175535656915705959,
        1049137689062035487,
    ]:
        message = makeplays_challenge_formatting(message)
    elif message.channel.id in [
        1188201803783876638,
        1164747583638491156,
        1204596671636443223,
    ]:
        message = makeplays_main_formatting(message)
    elif message.channel.id in [
        1195073059770605568,
        1175925024503378070,
        1168198165250441256,
    ]:
        message = bishop_formatting(message)
    elif message.channel.id in [897625103020490773]:
        message = theta_warrior_elite(message)
    elif message.channel.id in [
        1152082112032292896,
        884971446802219048,
        1209855531758395423,
        1210140760800763914,
        1132823605688938567,
    ]:
        message = kingmaker_main_formatting(message)
    elif message.channel.id in [
        1139700590339969036,
        1184315907376431114,
        1183711389777399808,
    ]:
        message = ddking_formatting(message)
    elif message.channel.id in [1102753361566122064, 977025121292259328]:
        message = crimson_formatting(message)
    elif message.channel.id in [1209854873344938044]:
        message = prophet_formatting(message)
    elif message.channel.id in [1214652173171040256]:
        message = jpa_formatting(message)
    elif message.channel.id in [1216951944933933137]:
        message = prophi_alerts(message)
    elif message.channel.id in [1272519008180240464]:
        message = clark_alerts(message)
    elif message.channel.id in [
        968629663394058270,
        1141877368877760552,
        1239936855370108948,
    ]:
        message = wolfwebull_formatting(message)
    elif message.channel.id in [1187162844362448896, 1189180874265210961]:
        message = nvstly_alerts(message)
    elif message.channel.id in [1244040902582865937]:
        message = cblast_alerts(message)
    elif message.channel.id in [1286022517869514874]:
        message = brando_trades(message)
    elif message.channel.id in [1235324290426081423]:
        message = chis_formatting(message)
    elif message.channel.id in [986816019295252500, 904535347331989514]:
        message = abi_formatting(message)
    elif message.channel.id in [872226993557606440]:
        message = mikeinvesting_trades(message)
    elif message.channel.id in [
        140295293546659840,
        815942180945920020,
        1188480300381110272,
    ]:
        message = jb_trades(message)
    elif message.guild.id in [
        826258453391081524,
        1093339706260979822,
        1072553858053701793,
        898981804478980166,
        682259216861626378,
    ]:
        message = aurora_trading_formatting(message)
    else:
        message = embed_to_content(message)
    return message


# Enhanced position tracking for Bear's alerts (persisted daily)
# Structure: {contract_key: {"ticker": str, "strike": str, "type": str, "expiry": str,
#                             "status": "entry|trim1|trim2|runners|closed", "entry_price": float}}
import json
from datetime import datetime as _dt
from pathlib import Path as _Path

BEAR_STATE_FILE = _Path(__file__).parent.parent / "data" / "bear_positions.json"
BEAR_POSITIONS = {}
BEAR_STATE_DATE = None


def _contract_key(ticker: str, strike: str, otype: str, exp_date: str) -> str:
    """Generate unique key for contract tracking"""
    return f"{ticker.upper()} {str(strike).upper()}{otype.upper()} {exp_date}"


def _load_bear_positions():
    """Load Bear position state from JSON file with daily reset"""
    global BEAR_POSITIONS, BEAR_STATE_DATE
    try:
        if BEAR_STATE_FILE.exists():
            with open(BEAR_STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            BEAR_STATE_DATE = data.get("date")
            # Reset if stale (different day)
            today = _dt.utcnow().strftime("%Y-%m-%d")
            if BEAR_STATE_DATE != today:
                BEAR_POSITIONS = {}
                BEAR_STATE_DATE = today
            else:
                BEAR_POSITIONS = data.get("positions", {})
        else:
            BEAR_STATE_DATE = _dt.utcnow().strftime("%Y-%m-%d")
    except Exception:
        # Fail silently; keep in-memory state only
        BEAR_POSITIONS = {}
        BEAR_STATE_DATE = _dt.utcnow().strftime("%Y-%m-%d")


def _save_bear_positions():
    """Persist Bear position state to JSON file"""
    try:
        BEAR_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(BEAR_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"date": BEAR_STATE_DATE, "positions": BEAR_POSITIONS}, f, indent=2
            )
    except Exception:
        pass


def _register_position(
    ticker: str, strike: str, otype: str, exp_date: str, price: float = None
):
    """Register new position in BEAR_POSITIONS with 'entry' status"""
    key = _contract_key(ticker, strike, otype, exp_date)
    BEAR_POSITIONS[key] = {
        "ticker": ticker.upper(),
        "strike": str(strike).upper(),
        "type": otype.upper(),
        "expiry": exp_date,
        "status": "entry",
        "entry_price": price,
    }
    _save_bear_positions()


def _update_position_status(
    ticker: str, strike: str, otype: str, exp_date: str, new_status: str
):
    """Update position status (entry -> trim1 -> trim2 -> runners -> closed)"""
    key = _contract_key(ticker, strike, otype, exp_date)
    if key in BEAR_POSITIONS:
        BEAR_POSITIONS[key]["status"] = new_status
        _save_bear_positions()


def _get_positions_by_ticker_status(ticker: str, status: str):
    """Get all positions for a ticker with specific status"""
    return [
        (key, pos)
        for key, pos in BEAR_POSITIONS.items()
        if pos["ticker"] == ticker.upper() and pos["status"] == status
    ]


def _get_most_recent_active_position():
    """Get the most recently added position that isn't closed"""
    # Return positions in reverse order (most recent first) that aren't closed
    active_positions = [
        (key, pos) for key, pos in BEAR_POSITIONS.items() if pos["status"] != "closed"
    ]
    return active_positions[-1] if active_positions else (None, None)


# Load state once on import
_load_bear_positions()


def embed_to_content(message_):
    """Convert embed message to content message"""

    message = MessageCopy(message_)
    if (message.content.startswith("<@") and len(message.content.split())) == 1 or (
        message.content.startswith("@") and len(message.content.split())
    ):
        if message.embeds:
            message.content = message.embeds[0].description
    return message


def tradeproelite_formatting(message_):
    """
    Reformat Discord message from TPE to change generate alerts bot to author
    TPE guild id: 836435995854897193
    """
    message = MessageCopy(message_)
    # Change bot to author
    if message.author.name == "EnhancedMarket":
        message.author.name = "enhancedmarket"
        message.author.discriminator = "0"
    elif message.author.name == "Alertsify":
        message = MessageCopy(message_)
        message.author.name = message.embeds[0].author.name
        message.content = message.embeds[0].description
        message.author.discriminator = "0"
    return message


def prosperitytrades_formatting(message_):
    """
    Reformat Discord message from PT to change generate alerts bot to author
    """
    # Don't do anything if not Xtrade message
    if message_.guild.id != 1204779568058335232:
        return message_

    # Change bot to author
    if (
        message_.author.name.lower() == "vader-alerts"
        or message_.author.name == "RedSaberSwings"
    ):
        message = MessageCopy(message_)
        message_.author.name = "lordvader32"
        message_.author.discriminator = "0"
        return message_

    return message_


def flint_formatting(message_):
    """
    Reformat Discord message from Flint
    """
    message = MessageCopy(message_)
    alert = ""
    for mb in message.embeds:
        if mb.description:
            alert += mb.description
    if not len(alert):
        alert = message.content
    if len(alert):
        pattern = r"([A-Z]+)\s*(\d+[.\d+]*[c|p|C|P])\s(\d{1,2}\/\d{1,2})\s*@\s*(\d+(?:[.]\d+)?|\.\d+)"
        match = re.search(pattern, alert, re.IGNORECASE)
        if match:
            out = match.groups()
            if len(out) == 4:
                ticker, strike, msg_date, price = out
            elif len(out) == 3:
                ticker, strike, price = out
                msg_date = message.created_at.strftime("%m/%d")
            else:
                print("ERROR: wrong number of groups in flint_formatting")
                return message
            ext = alert.split(price)[-1]
            alert = f"BTO {ticker} {strike.upper()} {msg_date} @{price} {ext}"
        message.content = alert
    return message


def jpm_formatting(message_):
    """
    Reformat Discord message from jpm
    """
    message = MessageCopy(message_)
    alert = ""
    for mb in message.embeds:
        if mb.description:
            alert += mb.description
    if not len(alert):
        alert = message.content
    if len(alert):
        pattern = r"([A-Z]+)\s(\d{1,2}\/\d{1,2})\s*(\d+[.\d+]*[c|p|C|P])\s*@\s*(\d+(?:[.]\d+)?|\.\d+)"
        match = re.search(pattern, alert, re.IGNORECASE)
        if match:
            ticker, expdate, strike, price = match.groups()
            # BTO always have SL
            action = "BTO" if "Open" in alert else "STC"
            ext = "" if action == "BTO" or " out" in alert else f" trim "
            if "lotto" in alert.lower():
                ext += " lotto"
            if "trim" in ext:
                ext += alert.split(price)[-1]
            alert = f"{action} {ticker} {strike.upper()} {expdate} @{price} {ext}"
        message.content = alert
    return message


def clutch_trades(message_):
    """
    Reformat Discord message from clutch trades
    """
    message = MessageCopy(message_)
    alert = ""
    for mb in message.embeds:
        if mb.description:
            alert += mb.description
    if not len(alert):
        alert = message.content

    if len(alert):
        pattern = r"(\d{1,2}\/\d{1,2})\s*([A-Z]+)\s(\d+[.\d+]*[c|p|C|P])\s*(\d+(?:[.]\d+)?|\.\d+)"
        match = re.search(pattern, alert, re.IGNORECASE)
        if match:
            expdate, ticker, strike, price = match.groups()
            # BTO always have SL
            action = "BTO"
            alert = f"{action} {ticker} {strike.upper()} {expdate} @{price}"
        message.content = alert
    return message


def brando_trades(message_):
    """
    Reformat Discord message from brando trades
    """
    message = MessageCopy(message_)
    alert = ""
    for mb in message.embeds:
        if mb.description:
            alert += mb.description
    if not len(alert):
        alert = message.content

    if "BOUGHT" in alert:
        pattern = r"BOUGHT \|*\s*(\w+)\s+(NOV|DEC|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT)\s*(\d{1,2})\s*(\d+\.?\d*[cCpP])\s*\$?(\d+\.\d+)"
        match = re.search(pattern, alert, re.IGNORECASE)
        if match:
            ticker, month, day, strike, price = match.groups()
            if month == "DEC":
                year = "24"
            else:
                year = "25"
            expdate = convert_date(f"{day.zfill(2)}{month[:3].upper()}{year}")

            action = "BTO"
            alert = f"{action} {ticker.upper()} {strike.upper()} {expdate} @{price}"
        else:
            alert = alert.replace("$", " weeklies @$").replace("BOUGHT", "BTO")
            alert = format_0dte_weeklies(alert, message, False)
    elif "SOLD" in alert:
        pattern = r"SOLD \|*\s*(\w+)\s+(NOV|DEC|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT)\s*(\d{1,2})\s*(\d+\.?\d*[cCpP])\s*\$?(\d+\.\d+)\s*(1\/2|1\/4|2\/3)?"
        match = re.search(pattern, alert, re.IGNORECASE)
        if match:
            ticker, month, day, strike, price, position = match.groups()
            if month == "DEC":
                year = "24"
            else:
                year = "25"
            expdate = convert_date(f"{day.zfill(2)}{month[:3].upper()}{year}")

            action = "STC"
            position = position + " POS" if position else "all out"
            alert = f"{action} {ticker.upper()} {strike.upper()} {expdate} @{price} {position}"
        else:
            alert = alert.replace("$", " weeklies @$").replace("SOLD", "STC")
            alert += (
                " 1/2 POS"
                if "1/2 POS" in alert
                else " 1/4 POS"
                if "1/4 POS" in alert
                else " 1/3 POS"
                if "1/3 POS" in alert
                else " all out"
            )
            alert = format_0dte_weeklies(alert, message, False)
    message.content = alert
    return message


def mikeinvesting_trades(message_):
    """
    Reformat Discord message from brando trades
    """
    message = MessageCopy(message_)
    alert = message.content

    # Define the regular expression pattern
    pattern = r"""
    \$(?P<ticker>[A-Z]+)⚡️\s*                # Ticker, e.g., $SPY⚡️
    \$(?P<strike>[\d\.]+)\s(?P<side>[A-Z]+S)\s*  # Strike and side, e.g., $593 CALLS
    EXPIRATION\s(?P<expiration>\d{1,2}/\d{1,2}/\d{4})\s*  # Expiration, e.g., 1/3/2025
    \$(?P<entry_price>[\d\.]+)\sEntry\s*    # Entry price, e.g., $.12 or $1.23 Entry
    \$(?P<target_price>[\d\.]+)\sTARGET\s🎯  # Target price, e.g., $.3 or $10.45 TARGET 🎯
    """

    regex = re.compile(pattern, re.VERBOSE)

    match = regex.search(message.content)
    if match:
        data = match.groupdict()
        alert = "BTO {ticker} {strike}{side[0]} {expiration} @{entry_price} PT: {target_price}".format(
            **data
        )
        if "LOTTO" in message.content:
            alert += " LOTTO PLAY"
        elif "SUPPORT" in message.content:
            alert += " SUPPORT PLAY"

    message.content = alert
    return message


def jb_trades(message_):
    """
    Reformat Discord message from brando trades
    """
    message = MessageCopy(message_)
    alert = message.content
    month_mapping = {
        "JAN": "01",
        "FEB": "02",
        "MAR": "03",
        "APR": "04",
        "MAY": "05",
        "JUN": "06",
        "JUL": "07",
        "AUG": "08",
        "SEP": "09",
        "OCT": "10",
        "NOV": "11",
        "DEC": "12",
    }

    pattern = r"([A-Z]+)\s+([A-Z,a-z]*)\s+(\d{1,2})(?:th|st|nd|rd)\s+\$([\d\.]+)\s+(calls|puts)\s+@\s+\$*([\d\.]+)"
    match = re.search(pattern, alert)
    if match:
        ticker, month, day, strike, otype, price = match.groups()
        exp_date = f"{month_mapping[month.upper()]}/{day.zfill(2)}"
        if "out" in alert:
            alert = f"STC {ticker} {strike.upper()}{otype[0]} {exp_date} @{price}"
            if any(x.lower() in alert for x in ["Out some", "Out more", "Out a few"]):
                alert += " 1/3 POS"
        else:
            alert = f"BTO {ticker} {strike.upper()}{otype[0]} {exp_date} @{price}"
        message.content = alert
    return message


def kent_formatting(message_):
    """
    Reformat Discord message from Kent
    """
    message = MessageCopy(message_)
    alert = ""
    for mb in message.embeds:
        if mb.description:
            alert += mb.description
    if len(alert):
        message.content = alert
    return message


def sirgoldman_formatting(message_):
    """
    Reformat Discord message from sirgoldman
    """
    message = MessageCopy(message_)
    for mb in message.embeds:
        if mb.description:
            if mb.title.upper() == "ENTRY":
                pattern = (
                    r"\$([A-Z]+)\s*(\d+[.\d+]*[c|p|C|P])\s*@\s*(\d+(?:[.]\d+)?|\.\d+)"
                )
                match = re.search(pattern, mb.description, re.IGNORECASE)
                if match:
                    ticker, strike, price = match.groups()
                    msg_date = message.created_at.strftime("%m/%d")
                    ext = mb.description.split(price)[-1]
                    alert = f"BTO {ticker} {strike.upper()} {msg_date} @{price} {ext}"
                else:
                    alert = f"{mb.title}: {mb.description}"
            else:
                alert = f"{mb.title}: {mb.description}"
            message.content = alert
    return message


def chis_formatting(message_):
    """
    Reformat Discord message from Chis
    """
    message = MessageCopy(message_)
    alert = message.content
    for mb in message.embeds:
        if mb.description:
            alert = mb.description
    msg_date = message.created_at.strftime("%m/%d")

    pattern = r"IN LOTTO (\d{3})([cpCP]) ([\d.]+)"
    match = re.search(pattern, alert, re.IGNORECASE)

    if match:
        strike, otype, price = match.groups()
        formatted_alert = f"BTO SPY {strike.upper()}{otype.upper()} {msg_date} @{price}"
        message.content = formatted_alert

    return message


def abi_formatting(message_):
    """
    Reformat Discord message from Abi
    """
    message = MessageCopy(message_)
    alert = message.content

    pattern_with_date = r"\$([A-Z]+)\s+(\d{1,2}/\d{1,2})\s+(\d+)([cCpP])\s+([\d.]+)"
    pattern_without_date = r"\$([A-Z]+)\s+(\d+)([cCpP])\s+([\d.]+)"

    match = re.search(pattern_with_date, alert, re.IGNORECASE)
    if match:
        ticker, exp_date, strike, otype, price = match.groups()
    else:
        match = re.search(pattern_without_date, alert, re.IGNORECASE)
        if match:
            ticker, strike, otype, price = match.groups()
            today = datetime.today()
            if today.weekday() == 4:
                exp_date = today.strftime("%m/%d")
            else:
                days_until_friday = (4 - today.weekday()) % 7
                upcoming_friday = today + timedelta(days=days_until_friday)
                exp_date = upcoming_friday.strftime("%m/%d")
        else:
            return message

    formatted_alert = (
        f"BTO {ticker.upper()} {strike}{otype.upper()} {exp_date} @{price}"
    )
    message.content = formatted_alert

    return message


def jpa_formatting(message_):
    """
    Reformat Discord message from JPA

    Bought $AMZN 177.5c for .95
    Bought $AAPL 180 calls for next week at 1.18
    Bought 3/1 $AAPL 180p for .62
    Bought $GOOGL 142c for .85
    or look for symbol end of msg
    """
    message = MessageCopy(message_)
    alert = ""
    for mb in message.embeds:
        if "Jpa" in mb.description:
            message.author.name = "JPA"
        if "Contract Found:" in mb.description:
            exp = r"([A-Z]+)_([\d]+)_([\d]+)_(C|P) Live Price: ([\d.]+) Alert Price: ([\d.]+)"
            match = re.search(exp, mb.description, re.IGNORECASE)
            if match:
                contract, expiration, strike, otype, live_price, alert_price = (
                    match.groups()
                )
                expiration = f"{expiration[:2]}/{expiration[2:4]}"

                if alert_price is not None or float(alert_price) > 0:
                    price = alert_price
                else:
                    price = live_price  # Use live price if we can't find the price in the content

                alert = f"BTO {contract} {strike}{otype} {expiration} @{price}"
                break  # Exit the loop once we've found and processed the contract information

    if not alert:
        # Fallback parsing if we didn't find the contract information
        exp = r"\$([A-Z]+) ([\d.]+)(c|p|C|P) for ([\d.]+)"
        match = re.search(exp, message.content, re.IGNORECASE)
        if match:
            contract, strike, otype, price = match.groups()
            expiration = message.created_at.strftime(
                "%m/%d"
            )  # Use current date if not specified
            alert = f"BTO {contract} {strike}{otype.upper()} {expiration} @{price}"

    message.content = alert
    return message


def nitro_formatting(message_):
    """
    Reformat Discord message from nitro trades
    """
    message = MessageCopy(message_)

    alert = ""
    for mb in message.embeds:
        if mb.description:
            alert += mb.description
    if not len(alert):
        alert = message.content
    if len(alert):
        if "Entry" in alert:
            contract_match = re.search(
                r"\*\*Contract:\*\*[ ]+([A-Z]+)[ ]+?(\d{1,2}\/\d{1,2})?[ ]*?\$?([0-9]+)([cCpP])",
                alert,
            )
            fill_match = re.search(r"\*\*Price:\*\* ?\$?([\d.]+)", alert)

            if contract_match:
                contract, exp_date, strike, otype = contract_match.groups()
                if fill_match is not None:
                    price = float(fill_match.groups()[0])
                else:
                    price = None
                if exp_date is None:
                    if contract in ["QQQ", "SPY", "IWM"]:
                        exp_date = "0DTE"
                    else:
                        exp_date = "Weeklies"
                bto = f"BTO {contract} {strike}{otype.upper()} {exp_date} @{price}"
                alert += format_0dte_weeklies(bto, message, False)

    if len(alert):
        message.content = alert
    return message


def diesel_formatting(message_):
    """
    Reformat Discord message from diesel trades
    """
    message = MessageCopy(message_)

    if message.content is None:
        return message

    alert = message.content
    pattern = r"BTO\s+([A-Z]+)\s+([\d.]+)([c|p])\s*(\d{1,2}\/\d{1,2})?\s+@\s*([\d.]+)"
    match = re.search(pattern, alert, re.IGNORECASE)
    if match:
        ticker, strike, otype, expDate, price = match.groups()
        if expDate is None:
            bto = f"BTO {ticker} {strike.upper()}{otype[0]} 0DTE @{price}"
            alert = format_0dte_weeklies(bto, message, False)
        else:
            alert += f"BTO {ticker} {strike.upper()}{otype[0]} {expDate} @{price}"

    if len(alert):
        message.content = alert
    return message


def owl_formatting(message_):
    """
    Reformat Discord message from ownl trades
    """
    message = MessageCopy(message_)
    if len(message.embeds[0].description):
        pattern = (
            r"TICKER: ([A-Z]+)\nSTRIKE: (\d+[C|P])\nPRICE: ([\d.]+)\nEXP: (\d{2}/\d{2})"
        )
        match = re.search(pattern, message.embeds[0].description)
        if match:
            ticker = match.group(1)
            strike = match.group(2)
            price = match.group(3)
            exp_date = match.group(4)
            extra = message.embeds[0].description.split(exp_date)[-1].replace("\n", " ")
            message.content = f"BTO {ticker} {strike} {exp_date} @{price} {extra}"
            message.author.name = message.embeds[0].author.name
        else:
            pattern = r"([A-Z]+) (\d+[CP]) (\d{1,2}/\d{1,2}exp) ([\d.]+)"
            match = re.search(pattern, message.embeds[0].description)
            if match:
                ticker = match.group(1)
                strike = match.group(2)
                exp_date = match.group(3)
                price = match.group(4)
                extra = (
                    message.embeds[0].description.split(exp_date)[-1].replace("\n", " ")
                )
                message.content = f"BTO {ticker} {strike} {exp_date} @{price} {extra}"
                message.author.name = message.embeds[0].author.name

    elif message.content.startswith(".bto"):
        pattern = (
            r"TICKER: ([A-Z]+)\nSTRIKE: (\d+[C|P])\nPRICE: ([\d.]+)\nEXP: (\d{2}/\d{2})"
        )
        match = re.search(pattern, message.content)
        if match:
            ticker = match.group(1)
            strike = match.group(2)
            price = match.group(3)
            exp_date = match.group(4)
            extra = message.content.split(exp_date)[-1].replace("\n", " ")
            message.content = f"BTO {ticker} {strike} {exp_date} @{price} {extra}"
    return message


def xtrades_formatting(message_):
    """
    Reformat Discord message from Xtrades to a sandard alert format
    Xtrades guild id: 542224582317441034
    """
    # Don't do anything if not Xtrade message
    if (
        message_.guild.id != 542224582317441034
        or message_.channel.id == 993892865824542820
    ):
        return message_

    # return None if not Xtrade bot
    if message_.author.name != "Xcapture":
        message_.content = (
            message_.content.replace("BTO", "BTO_msg")
            .replace("STC", "STC_msg")
            .replace("STO", "STO_msg")
            .replace("BTC", "BTC_msg")
        )
        return message_

    message = MessageCopy(message_)

    # get action and author
    actions = {
        "entered long": "BTO",
        "entered long from the web platform.": "BTO",
        "averaged long": "BTO_avg",
        "added an update from the web platform.": "exitupdate",
        "STOPPED OUT:": "STC",
        "STOPPED IN PROFIT:": "STC",
        "closed long from the web platform.": "STC",
        "closed long": "STC",
        "entered short": "STO",
        "entered short from the web platform.": "STO",
        "covered short from the web platform.": "BTC",
        "covered short": "BTC",
    }
    author_name = message.embeds[0].author.name
    if author_name is None:
        return message
    for action_str, action_code in actions.items():
        if action_str in author_name:
            action = action_code
            pattern = re.compile(f"(.+?) {action_str}")
            match = pattern.match(author_name)
            if match:
                author = match.group(1)
                message.author.name = author
                message.author.discriminator = "0"
                message.author.bot = False
                break
    else:
        print("ERROR: unknown action")
        print(message.embeds[0].author.name)
        return message

    # format alert
    if action in ["BTO", "STC", "STO", "BTC"]:
        pattern = re.compile(
            r"(?:\:\S+ )?(\w+) (\w+)(?: (\w+ \d+ \d+) \$?(\d+\.\d+) (\w+))? @ \$?(\d+(?:\.\d+)?)",
            re.IGNORECASE,
        )
        msg = (
            message.embeds[0].title.replace("**", "").replace("_", "").replace("¤", "$")
        )
        match = pattern.match(msg)
        if match:
            direction, stock, expiration_date, strike, option_type, price = (
                match.groups()
            )

            market_pattern = re.compile(r"(?:market|current) : \$(\d+(?:\.\d+)?)")
            match = market_pattern.search(msg)
            if match:
                price = match.group(1)
            else:
                price = f"{price} (alert price)"

            if strike is not None:
                expiration_date = datetime.strptime(
                    expiration_date, "%b %d %Y"
                ).strftime("%m/%d/%y")
                alert = f"{action} {stock} {strike.replace('.00', '')}{option_type[0]} {expiration_date} @{price}"
            else:
                alert = f"{action} {stock} @{price}"

            # add SL and TP and other fields
            for mb in message.embeds:
                for fld in mb.fields:
                    if hasattr(fld, "value"):
                        alert += f" | {fld.name}: {fld.value}"
            descp = (
                message.embeds[0]
                .description.split("[VIEW DETAILS]")[0]
                .replace("\r\n", " ")
            )
            alert += f" | {descp}"

            message.content = alert
            return message
        print("no match", msg)
        return message
    else:
        alert = ""
        # add Sl and TP and other fields
        for mb in message.embeds:
            for fld in mb.fields:
                if hasattr(fld, "value"):
                    alert += f" | {fld.name}: {fld.value}"
        descp = (
            message.embeds[0]
            .description.split("[VIEW DETAILS]")[0]
            .replace("\r\n", " ")
        )
        alert += f" | {descp}"
        message.content = alert
        return message


def makeplays_challenge_formatting(message_):
    """
    Reformat Discord message from makeplay trades
    """
    message = MessageCopy(message_)
    print("formatting makeplays")
    if message.content is None:
        return message

    alert = message.content
    alert = alert.replace("weekly contract", "weeklies").replace(" at ", " @ ")
    alert = format_0dte_weeklies(alert, message, False)

    # strike then exp date
    pattern = r"(?:BTO)?\s*([\d]+)?\s*([A-Z]+)\s+([\d.]+)([C|P])\s*(\d{1,2}\/\d{1,2}(?:\/\d{2,4})?)?\s+@?\s*([\d.]+)"
    match = re.search(pattern, alert, re.IGNORECASE)
    # exp date then strike
    strike_first = True
    if match is None:
        pattern = r"(?:BTO)?\s*([\d]+)?\s+([A-Z]+)\s*(\d{1,2}\/\d{1,2}(?:\/\d{2,4})?)?\s+([\d.]+)([C|P])\s+@\s*([\d.]+)"
        match = re.search(pattern, alert, re.IGNORECASE)
        strike_first = False

    if match:
        if strike_first:
            qty, ticker, strike, otype, expDate, price = match.groups()
        else:
            qty, ticker, expDate, strike, otype, price = match.groups()
        if qty is None:
            qty = ""
        else:
            qty = f" {qty}"
        if expDate is None:
            if ticker in ["SPY", "QQQ", "IWM", "DIA"]:
                bto = f"BTO{qty} {ticker} {strike.upper()}{otype[0]} 0DTE @{price}"
            else:
                bto = f"BTO{qty} {ticker} {strike.upper()}{otype[0]} weeklies @{price}"
            alert = format_0dte_weeklies(bto, message, False)
        else:
            alert = f"BTO{qty} {ticker} {strike.upper()}{otype[0]} {expDate} @{price}"

    message.content = alert
    return message


def makeplays_main_formatting(message_):
    """
    Reformat Discord message from makeplays
    """
    message = MessageCopy(message_)

    alert = ""
    for mb in message.embeds:
        if mb.title == "Open":
            alert = mb.description.replace(" at ", " @ ")
            if "0DTE" in alert.upper() or "1DTE" in alert.upper():
                alert = format_0dte_weeklies(alert, message, False)
            if "BTO" not in alert:
                alert = f"BTO {alert}"
        elif mb.title.startswith("Close"):
            alert = mb.description.replace(" at ", " @ ")
            if "STC" not in alert:
                alert = f"STC {alert}"
        else:
            alert = f"{mb.title}: {mb.description}"

    message.content = alert
    return message


def bishop_formatting(message_):
    """
    Reformat Discord message from bishop
    """
    message = MessageCopy(message_)

    alert = ""
    for mb in message.embeds:
        if mb.description:
            alert += mb.description
    if not len(alert):
        alert = message.content
        print("bishop", alert)

    match = False
    if "I'm entering" in alert:
        action = "BTO"
        match = True
        extra = (
            alert.split("@$")[1]
            .split("\r\n\r\n*These are ONLY my opinions")[0]
            .replace("\r\n\r\n", " ")
        )
        pattern = r"\*\*Option:\*\* ([A-Z]+) (\d.+) ([PC]) (\d+\/\d+)\\r\\n\\r\\n\*\*Entry:\*\* @\$(\d+\.\d+)"
    elif "Trimming" in alert:
        action = "STC"
        match = True
        extra = alert.split("\r\n\r\n*These are ONLY my opinions")[0].replace(
            "\r\n\r\n", " "
        )
        pattern = r"([A-Z]+) (\d.+) ([PC]) (\d+\/\d+) @\$(\d+\.\d+)"

    if match:
        match = re.search(pattern, alert, re.IGNORECASE)
        if match:
            ticker, strike, otype, expdate, price = match.groups()
            extra = extra.replace(price, "")
            alert = (
                f"{action} {ticker} {strike.upper()}{otype} {expdate} @{price} {extra}"
            )
            if "Trimming" in alert:
                alert += " trim"

    if len(alert):
        message.content = alert
    return message


def convert_date(input_date):
    # Map month abbreviations to their numeric representation
    month_mapping = {
        "JAN": "01",
        "FEB": "02",
        "MAR": "03",
        "APR": "04",
        "MAY": "05",
        "JUN": "06",
        "JUL": "07",
        "AUG": "08",
        "SEP": "09",
        "OCT": "10",
        "NOV": "11",
        "DEC": "12",
    }
    # Extract day, month abbreviation, and year
    day = input_date[:-5]
    month_abbrev = input_date[-5:-2]
    year = input_date[-2:]
    # Convert month abbreviation to numeric representation
    month = month_mapping.get(month_abbrev.upper(), "00")
    converted_date = f"{month}/{day}/20{year}"
    return converted_date


def theta_warrior_elite(message_):
    if not message_.content:
        return message_

    message = MessageCopy(message_)
    alert = message.content

    if alert is None:
        return message

    pattern = re.search(
        r"\$(\w+).\S*\s*(BTO|STC)\s+(\d{1,2}\w{3}\d{2})\s+([\d.]+)([CPcp])\s+(?:at|@)\s+\$([\d.]+)",
        alert,
    )
    if pattern:
        ticker, action, exp_date, strike, otype, price = pattern.groups()
        exp_date = convert_date(exp_date)
        if action == "BTO":
            alert = f"{action} {ticker} {strike}{otype} {exp_date} @{price}"
        elif action == "STC":
            alert = f"{action} {ticker} {strike}{otype} {exp_date} @{price}"
            if "trim" in message.content.lower():
                alert += " trim"

            alert = format_0dte_weeklies(alert, message, False)
    if len(alert):
        message.content = alert
    return message


def format_0dte_weeklies(contract, message, remove_price=True):
    "remove price when stc title is bto"
    if "0DTE" in contract.upper():
        msg_date = message.created_at.strftime("%m/%d")
        contract = re.sub(r"0DTE", msg_date, contract, flags=re.IGNORECASE)
        if remove_price:
            contract = contract.split(" @")[0]
    elif "1DTE" in contract.upper():
        msg_date = message.created_at
        msg_date += timedelta(days=1)
        msg_date = msg_date.strftime("%m/%d")
        contract = re.sub(r"1DTE", msg_date, contract, flags=re.IGNORECASE)
        if remove_price:
            contract = contract.split(" @")[0]
    elif "weeklies" in contract.lower() or "next week" in contract.lower():
        msg_date = message.created_at
        days_until_friday = (4 - msg_date.weekday() + 7) % 7
        patt = "Weeklies"
        if "NEXT WEEK" in contract.upper():
            days_until_friday += 7  # Move to next week
            patt = "Next Week"

        msg_date += timedelta(days=days_until_friday)
        msg_date = msg_date.strftime("%m/%d")
        contract = re.sub(patt, msg_date, contract, flags=re.IGNORECASE)
        if remove_price:
            contract = contract.split(" @")[0]
    return contract


def aurora_trading_formatting(message_):
    """
    Reformat Discord message from aurora_trading to content message
    """
    message = MessageCopy(message_)
    # format Bryce trades
    if message_.channel.id in [
        846415903671320598,
        1093340247057772654,
        953812898059276369,
    ]:
        message.content = format_alert_date_price(message.content)
    # format ace trades
    elif message_.channel.id == 885627509121618010:
        alert = ""
        for mb in message.embeds:
            if mb.title == "Options Entry":
                description = mb.description
                # Extract the required information using regex
                contract_match = re.search(
                    r"\*\*\[🎟️\] Contract:\*\* __([^_]+)__", description
                )
                fill_match = re.search(r"\*\*\[🍉\] My Fill:\*\* ([\d.]+)", description)
                risk_match = re.search(r"\*\*\[🚨\]  Risk:\*\* ([\d/]+)", description)
                extra_info_match = re.search(
                    r"\*\*\[🗨️\] Comment:\*\* ([^\n]+)", description
                )

                if contract_match:
                    contract = contract_match.group(1).strip().replace(" - ", " ")
                    # Check for 0DTE and replace with today's date
                    contract = format_0dte_weeklies(contract, message)
                    contract = format_alert_date_price(contract)
                    alert += f"{contract}"
                if fill_match:
                    fill = fill_match.group(1).strip()
                    alert += f" @{fill}"
                if risk_match:
                    risk = risk_match.group(1).strip()
                    alert += f" risk: {risk}"
                if extra_info_match:
                    extra_info = extra_info_match.group(1).strip()
                    alert += f" | comment: {extra_info}"
            elif mb.title in ["Options Close", "Options Scale"]:
                description = mb.description
                # Extract the required information using regex
                contract_match = re.search(
                    r"\*\*\[🎟️\] Contract:\*\* __([^_]+)__", description
                )
                fill_match = re.search(
                    r"\*\*\[✂️] Scaling Price:\*\* ([\d.]+)", description
                )
                extra_info_match = re.search(
                    r"\*\*\[🗨️\] Comment:\*\* ([^\n]+)", description
                )

                if contract_match:
                    contract = contract_match.group(1).strip().replace(" - ", " ")
                    # Check for 0DTE and weeklies
                    contract = format_0dte_weeklies(contract, message)
                    contract = format_alert_date_price(contract)
                    alert += f"{contract}"
                if fill_match:
                    fill = fill_match.group(1).strip()
                    alert += f" @{fill}"
                if extra_info_match:
                    extra_info = extra_info_match.group(1).strip()
                    alert += f" | comment: {extra_info}"
                if mb.title == "Options Scale":
                    alert += " | partial scale"

            elif mb.description:
                alert += f"(not parsed) {mb.description}"
        if len(alert):
            message.content = alert
    # format demon trades
    elif message_.channel.id in [
        886669912389607504,
        1072553859454599197,
        904396043498709072,
    ]:
        contract = format_0dte_weeklies(message.content, message, False)
        message.content = format_alert_date_price(contract)

    return message


def oculus_alerts(message_):
    """
    Reformat Discord message from oculus to content message
    """

    if not message_.content:
        return message_

    message = MessageCopy(message_)
    alert = message.content

    if "%" in alert:  # just status update
        return message

    if "(0dte)" in alert.lower():
        alert = alert.replace("(0dte)", "0DTE")
        alert = format_0dte_weeklies(alert, message, remove_price=False)

    pattern = r"\$(\w+)\s+\$?(\d[\d,]+)\s+(\w+)\s+(\d{1,2}\/\d{1,2}(?:\/\d{2,4})?)\s+@([\d.]+)"
    match = re.search(pattern, alert, re.IGNORECASE)
    if match:
        ticker, strike, otype, expDate, price = match.groups()
        alert = f"BTO {ticker} {strike.upper()}{otype[0]} {expDate} @{price}"
        message.content = alert
    return message


def cblast_alerts(message_):
    """
    Reformat Discord message from cblast to content message
    """
    message = MessageCopy(message_)
    alert = message.content
    if not alert:
        return message

    # format:  $AI 29c 10/18 at 0.16
    pattern = r"\$([A-Z]+)\s+(\d+)([c|p|C|P])\s+(\d{1,2}\/\d{1,2})\s+at\s+([\d.]+)"
    match = re.search(pattern, alert, re.IGNORECASE)
    if match:
        ticker, strike, otype, expDate, price = match.groups()
        alert = f"BTO {ticker} {strike.upper()}{otype[0]} {expDate} @{price}"
        message.content = alert
    return message


def eclipse_alerts(message_):
    """
    Reformat Discord message from eclipse to content message
    """
    if not message_.content:
        return message_

    message = MessageCopy(message_)
    alert = message.content
    pattern = r"([A-Z]+)\s*(\d+[.\d+]*[c|p|C|P])\s*(\d{1,2}\/\d{1,2})?\s*@\s*(\d+(?:[.]\d+)?|\.\d+)"
    match = re.search(pattern, alert, re.IGNORECASE)
    if match:
        ticker, strike, expDate, price = match.groups()
        qty = re.search(r"(\d+)\s*Contracts", alert, re.IGNORECASE)
        qty = qty.group(1) if qty else "1"
        chall = ""
        if "Challenge Account" in alert:
            chall += " | Challenge Account"
        alert = f"BTO {qty} {ticker} {strike.upper()} {expDate} @{price}{chall}"
    else:  # date might come first
        pattern = r"([A-Z]+)\s*(\d{1,2}\/\d{1,2})?\s*(\d+[.\d+]*[c|p|C|P])\s*@\s*(\d+(?:[.]\d+)?|\.\d+)"
        match = re.search(pattern, alert, re.IGNORECASE)
        if match:
            ticker, expDate, strike, price = match.groups()
            qty = re.search(r"(\d+)\s*Contracts", alert, re.IGNORECASE)
            qty = qty.group(1) if qty else "1"
            chall = ""
            if "Challenge Account" in alert:
                chall += " | Challenge Account"
            alert = f"BTO {qty} {ticker} {strike.upper()} {expDate} @{price}{chall}"
        else:  # diff format
            pattern = (
                r"\$?(\w+)\s+\$?([\d.]+)\s+(\w+)\s+(\d{1,2}\/\d{1,2})\s+@\s*([\d.]+)"
            )
            match = re.search(pattern, alert, re.IGNORECASE)
            if match:
                ticker, strike, otype, expDate, price = match.groups()
                qty = re.search(r"(\d+)\s*Contracts", alert, re.IGNORECASE)
                qty = qty.group(1) if qty else "1"
                alert = (
                    f"BTO {qty} {ticker} {strike.upper()}{otype[0]} {expDate} @{price}"
                )
            else:
                pattern = r"\$([A-Z]+)\s+([\d.]+)\s+(CALL|PUT)\s+(\d{1,2}\/\d{1,2})\s+\@\s*([\d.]+)"
                match = re.search(pattern, alert, re.IGNORECASE)
                if match:
                    ticker, strike, otype, expDate, price = match.groups()
                    alert = (
                        f"BTO {ticker} {strike.upper()}{otype[0]} {expDate} @{price}"
                    )
                else:
                    pattern = r"\$([A-Z]+)\s+(\d{1,2}\/\d{1,2})\s+\$*([\d.]+)\s+(CALL|PUT)\s+\@\s*([\d.]+)"
                    match = re.search(pattern, alert, re.IGNORECASE)
                    if match:
                        ticker, expDate, strike, otype, price = match.groups()
                        alert = f"BTO {ticker} {strike.upper()}{otype[0]} {expDate} @{price}"

    message.content = alert
    return message


def kingmaker_main_formatting(message_):
    """
    Reformat Discord message from makeplays
    """
    message = MessageCopy(message_)

    alert = ""
    for mb in message.embeds:
        if mb.title == "Open":
            alert = mb.description.replace(" buy ", " ").replace(" Buy ", " ")

            pattern = r"([A-Z]+)\s*(\d{1,2}\/\d{1,2}(?:\/\d{2,4})?)?\s+\$([\d.]+)\s+(Call|Calls|calls|Puts|puts)\s+@?\$?([\d.]+)"
            match = re.search(pattern, alert, re.IGNORECASE)
            if match:
                ticker, expDate, strike, otype, price = match.groups()
                alert = f"BTO {ticker} {strike.upper()}{otype[0].upper()} {expDate} @{price}"
        else:
            alert = f"{mb.title}: {mb.description}"
    if len(alert):
        message.content = alert
    return message


def ddking_formatting(message_):
    """
    Reformat Discord message from ddking
    """
    message = MessageCopy(message_)

    alert = ""
    for mb in message.embeds:
        if mb.title is not None and "NEW SIGNAL" in mb.title:
            alert = mb.description.replace(" buy ", " ").replace(" Buy ", " ")
        else:
            alert = f"{mb.title}: {mb.description}"

    if len(alert):
        message.content = alert
    return message


def wolfwebull_formatting(message_):
    """
    Reformat Discord message from wolfwebull_formatting
    """
    message = MessageCopy(message_)

    alert = ""
    for mb in message.embeds:
        if not mb.description:
            continue
        alert = mb.description.replace(" Call", "C").replace(" Put", "P")

        pattern = r"([A-Z]+)\s+\$([\d.]+)(C|P)\s+(\d{1,2}\/\d{1,2})?\s*@\s*([\d.]+)"
        match = re.search(pattern, alert, re.IGNORECASE)
        if match:
            ticker, strike, otype, expDate, price = match.groups()
            if expDate is None:
                expDate = "0DTE" if ticker in ["SPY", "QQQ"] else "weeklies"
            alert = f"BTO {ticker} {strike.upper()}{otype.upper()} {expDate} @{price}"
            alert = format_0dte_weeklies(alert, message, False)
        else:
            print("match not found for Wolf")

    if len(alert):
        message.content = alert
    return message


def crimson_formatting(message_):
    """
    Reformat Discord message from crimson
    """
    message = MessageCopy(message_)
    alert = ""
    for mb in message.embeds:
        if mb.description:
            alert += mb.description
    if not len(alert):
        alert = message.content

    pattern = (
        r"([A-Z]+)\s+([\d.]+)([p|c])\s+(\d{1,2}\/\d{1,2})(?:[A-Z0-9 ]*)?\s+([\d.]+)"
    )
    match = re.search(pattern, alert, re.IGNORECASE | re.DOTALL)
    if match:
        ticker, strike, otype, expDate, price = match.groups()
        alert = f"BTO {ticker} {strike}{otype.upper()} {expDate} @{price}"
    else:
        pattern = (
            r"([A-Z]+)\s+(\d{1,2}\/\d{1,2})\s+([\d.]+)([p|c])(?:[A-Z0-9 ]*)?\s+([\d.]+)"
        )
        match = re.search(pattern, alert, re.IGNORECASE | re.DOTALL)
        if match:
            ticker, expDate, strike, otype, price = match.groups()
            alert = f"BTO {ticker} {strike}{otype.upper()} {expDate} @{price}"

    if len(alert):
        message.content = alert
    return message


def prophet_formatting(message_):
    """
    Reformat Discord message from prophet
    """
    message = MessageCopy(message_)

    alert = ""
    for mb in message.embeds:
        if mb.title is not None and "OPENING " in mb.title:
            pattern = r"Contract:\s*([A-Z]+)\s*(\d{1,2}\/\d{1,2}(?:\/\d{2,4})?)?\s+([\d.]+)([C|P])\s+@\s*([\d.]+)"
            match = re.search(
                pattern, mb.description.replace("<", "@"), re.IGNORECASE | re.DOTALL
            )
            if match:
                ticker, expDate, strike, otype, price = match.groups()
                alert = f"BTO {ticker} {strike}{otype.upper()} {expDate} @{price}"
            else:
                alert = f"{mb.title}: {mb.description}"
        else:
            alert = f"{mb.title}: {mb.description}"

    if len(alert):
        message.content = alert
    return message


def clark_alerts(message_):
    if not message_.content:
        return message_

    message = MessageCopy(message_)
    message.content = message.content.replace("Im in", "BTO")
    return message


def moneymotive(message_):
    """
    Reformat Discord message from moneymotive to content message
    """
    if not message_.content:
        return message_

    message = MessageCopy(message_)
    alert = message.content

    if "%" in alert and ":rotating_light:" not in alert:  # just status update
        print("Moneymotive no '%' or no rotatig light")
        return message

    if ":rotating_light:" in alert and "/" not in alert and "0DTE" not in alert:
        alert = alert.replace(":rotating_light:", "0DTE :rotating_light:")
        message.content = alert

    if "0DTE" in alert:
        alert = format_0dte_weeklies(alert, message, remove_price=False)
        message.content = alert

    pattern = r"\$?(\w+)\s+([\d.]+)\s+(\w+)\s+(\d{1,2}\/\d{1,2})\s*\w*\s+@\s*([\d.]+)"
    match = re.search(pattern, alert, re.IGNORECASE)
    if match:
        ticker, strike, otype, expDate, price = match.groups()
        alert = f"BTO {ticker} {strike.upper()}{otype[0]} {expDate} @{price}"
        message.content = alert
    else:
        pattern = (
            r"\$?(\w+)\s+([\d.]+)\s+(\w+)\s+@\s+([\d.]+)\s+\w*\s*(\d{1,2}\/\d{1,2})"
        )
        match = re.search(pattern, alert, re.IGNORECASE)
        if match:
            ticker, strike, otype, price, expDate = match.groups()
            alert = f"BTO {ticker} {strike.upper()}{otype[0]} {expDate} @{price}"
            message.content = alert
    return message


def nvstly_alerts(message_):
    message = MessageCopy(message_)
    for mb in message.embeds:
        pattern = (
            r"(Short|Closed Short) - \[(\w+) @ \$([\d\.]+)\].*\*\*cmp:\*\* \$([\d\.]+)"
        )
        if mb.description is None:
            return message
        match = re.search(pattern, mb.description)
        if match:
            action = match.group(1)
            ticker = match.group(2)
            # price = match.group(3)
            cmp_value = match.group(4)
            action = "STO" if action == "Short" else "BTC"
            message.content = f"{action} {ticker} @ {cmp_value}"
            message.author.name = mb.author.name
            message.author.discriminator = "0"

    return message


def prophi_alerts(message_):
    # $dg 15 mar 24 $167.5c $3.35

    message = MessageCopy(message_)
    alert = ""

    for mb in message.embeds:
        message.author.name = mb.description.split(":")[0]

        exp = r"\$([A-Z]+) (\d{1,2} [A-Z]{3} \d{1,2}) \$([\d.]+)(c|p|C) \$([\d.]+)"
        match = re.search(exp, mb.description, re.IGNORECASE | re.DOTALL)
        if match:
            print("match for prophi")
            contract, expdate, strike, otype, price = match.groups()
            # day month scripted year to expdate

            expdate = convert_date(expdate.upper().replace(" ", ""))
            alert = f"BTO {contract.upper()} {strike}{otype.upper()} {expdate.replace('/2024', '')} @{price}"
        else:
            print("no match for prophi")
            alert = mb.description
    message.content = alert
    return message


def bear_alerts(message_):
    """
    Reformat Discord message from bear to content message
    Bear's Bot sends embeds - need to map bot to actual trader
    """
    message = MessageCopy(message_)

    # Map Bear's Bot to the actual trader
    # You can configure this mapping based on which trader is posting
    if message.author.name == "Bear's Bot":
        # Default mapping - update this to the actual trader name you want to follow
        message.author.name = "Bear-ish"  # or whatever the actual trader name is
        message.author.discriminator = "0033"

    alert = ""
    title = ""
    for mb in message.embeds:
        if mb.title:
            title += mb.title
        if mb.description:
            alert += mb.description

    # Normalize Unicode apostrophes to ASCII to stabilize matching (e.g., I’m -> I'm)
    alert = alert.replace("\u2019", "'")

    """ print(
        f"DEBUG bear_alerts: author={message.author.name}, alert_len={len(alert)}, title_len={len(title)}"
    )
    print(f"DEBUG bear_alerts: alert={alert}")
    print("---") """

    # Check for Entry first (BTO alerts) - Entry: indicates opening a position
    # Daytrade/LOTTO/Swing can be in title or description
    if "Entry:" in alert and any(
        p in (alert + title) for p in ["Daytrade", "LOTTO", "Swing"]
    ):
        type_al = [p for p in ["Daytrade", "LOTTO", "Swing"] if p in (alert + title)][0]

        # Try both formats: "Contract:  **" and "**Contract:**"
        contract_match = re.search(
            r"Contract:\s+\*\*([A-Z]+)\s+(\d{1,2}\/\d{1,2})\s+([\d.]+)([cCpP])\*\*",
            alert,
        )
        if contract_match is None:
            contract_match = re.search(
                r"\*\*Contract:\*\*\s+\$?([A-Z]+)\s+(\d{1,2}\/\d{1,2})\s+([\d.]+)([cCpP])",
                alert,
            )

        # Try alternate format with ticker and strike in different order
        if contract_match is None:
            contract_match = re.search(
                r"\*\*Ticker:\s+\$?([A-Z]+)\*\*.*\*\*Contract:\s+(\d{1,2}\/\d{1,2})\s+([\d.]+)([cCpP])",
                alert,
                re.DOTALL,
            )

        # Try to find entry price
        fill_match = re.search(r"Entry:\s+\*\*(\d+\.?\d*)\*\*", alert)
        if fill_match is None:
            fill_match = re.search(r"\*\*Entry:\*\*\s*\@?\$?\s*([\d.]+)", alert)

        if contract_match:
            contract, exp_date, strike, otype = contract_match.groups()
            if fill_match is not None:
                price = float(fill_match.groups()[0])
            else:
                price = None

            # Register new position with 'entry' status
            _register_position(contract, strike, otype, exp_date, price)

            alert = (
                f"BTO {contract} {strike}{otype.upper()} {exp_date} @{price} {type_al}"
            )
        else:
            # Keep original if can't parse
            message.content = alert
            return message

    # Bulk close: "Consider this a close on both QQQ/IWM" - close all runners for listed tickers
    elif re.search(r"consider this a close", alert, re.IGNORECASE):
        # Extract ticker list from patterns like:
        #   "close on both QQQ/IWM"
        #   "close on QQQ/IWM"
        #   "close on QQQ & IWM"
        tickers = []
        m_both = re.search(
            r"close on both\s+([A-Z]{1,5})[\\/ &]+([A-Z]{1,5})", alert, re.IGNORECASE
        )
        if m_both:
            tickers = [m_both.group(1).upper(), m_both.group(2).upper()]
        else:
            # Try multi-ticker pattern
            m_multi = re.search(
                r"close on\s+([A-Z]{1,5}(?:[\\/,& ]+[A-Z]{1,5})+)", alert, re.IGNORECASE
            )
            if m_multi:
                raw = m_multi.group(1)
                tickers = [
                    t.upper() for t in re.split(r"[\\/,& ]+", raw) if t and t.isupper()
                ]

        # If 'both' present but regex failed, close all positions with remaining runners (trim2 or runners status)
        if "both" in alert.lower() and not tickers:
            tickers = list(
                set(
                    pos["ticker"]
                    for pos in BEAR_POSITIONS.values()
                    if pos["status"] in ["trim2", "runners"]
                )
            )

        close_lines = []
        for ticker in tickers:
            # Close positions that have remaining 10% (trim2 or runners status)
            trim2_positions = _get_positions_by_ticker_status(ticker, "trim2")
            runner_positions = _get_positions_by_ticker_status(ticker, "runners")

            for key, pos in trim2_positions + runner_positions:
                # Close remaining 10% runners
                close_lines.append(
                    f"STC {pos['ticker']} {pos['strike']}{pos['type']} {pos['expiry']} @0 runners sold 10% final"
                )
                _update_position_status(
                    pos["ticker"], pos["strike"], pos["type"], pos["expiry"], "closed"
                )

        if close_lines:
            alert = "\n".join(close_lines)
        # If no runners found, leave alert unchanged (will fail to parse, which is expected)

    # Check for trim/close (STC alerts) - use specific patterns to avoid false positives in disclaimer
    # Note: Discord may use Unicode apostrophe ' (U+2019) instead of ASCII ' (U+0027)
    elif any(
        a in alert.lower()
        for a in [
            "i'm trimming",
            "trimming",
            "i'm closing",
            "closing",
            "full profit",
            "fully close",
            "de risking",  # partial trim without explicit contract
            "stopped out",  # exit due to stop loss
        ]
    ):
        # Trim/close detected

        # Try format: "**Contract:** QQQ 11/12 622P" (with space after colon)
        contract_match = re.search(
            r"\*\*Contract:\*\*\s+([A-Z]+)\s+(\d{1,2}\/\d{1,2})\s+([\d.]+)([cCpP])",
            alert,
        )

        # Try alternate format: "Contract:  **QQQ 11/12 622P**"
        if contract_match is None:
            contract_match = re.search(
                r"Contract:\s+\*\*([A-Z]+)\s+(\d{1,2}\/\d{1,2})\s+([\d.]+)([cCpP])\*\*",
                alert,
            )

        # Original format with $ sign
        if contract_match is None:
            contract_match = re.search(
                r"\*\*Contract:\*\*\s+\$([A-Z]+)\s+(\d{1,2}\/\d{1,2})\s+([\d.]+)([cCpP])",
                alert,
            )

        if contract_match:
            contract, exp_date, strike, otype = contract_match.groups()

            # Determine if this is a trim (vs a full close phrase)
            is_trim = ("I'm trimming" in alert) or ("trimming" in alert.lower())

            # Build a key for tracking position state
            key = _contract_key(contract, strike, otype, exp_date)

            # Get current position status
            current_status = BEAR_POSITIONS.get(key, {}).get("status", "unknown")

            # Extract profit percentage (supports patterns like 'for 52%' or 'Up **__105__**%')
            profit_match = re.search(r"for\s+(\d+)%", alert)
            if profit_match is None:
                profit_match = re.search(r"Up\s+[*_]*(__)?(\d+)[*_]*(__)?%", alert)
            profit_pct = None
            if profit_match:
                # second group contains digits in alternate pattern
                groups = profit_match.groups()
                if len(groups) == 1:
                    profit_pct = groups[0]
                elif len(groups) >= 2:
                    profit_pct = groups[1]

            if is_trim:
                # Transition states: entry -> trim1 -> trim2 -> runners
                if current_status == "entry":
                    # First trim: 45%
                    _update_position_status(contract, strike, otype, exp_date, "trim1")
                    alert = f"STC {contract} {strike}{otype.upper()} {exp_date} @0 trim sold 45%"
                    if profit_pct:
                        alert += f" up {profit_pct}%"
                elif current_status == "trim1":
                    # Second trim: 45%
                    _update_position_status(contract, strike, otype, exp_date, "trim2")
                    alert = f"STC {contract} {strike}{otype.upper()} {exp_date} @0 trim sold 45%"
                    if profit_pct:
                        alert += f" up {profit_pct}%"
                elif current_status == "trim2":
                    # Third+ trim: transition to runners (10% remain)
                    _update_position_status(
                        contract, strike, otype, exp_date, "runners"
                    )
                    alert = f"ExitUpdate {contract} {strike}{otype.upper()} {exp_date} runners (10% remain)"
                    if profit_pct:
                        alert += f" up {profit_pct}%"
                else:
                    # Already at runners or unknown state; keep as ExitUpdate
                    alert = f"ExitUpdate {contract} {strike}{otype.upper()} {exp_date} runners (10% remain)"
                    if profit_pct:
                        alert += f" up {profit_pct}%"
            else:
                # Non-trim close keywords present; full close
                _update_position_status(contract, strike, otype, exp_date, "closed")
                alert = f"STC {contract} {strike}{otype.upper()} {exp_date} @0"
                if profit_pct:
                    alert += f" up {profit_pct}%"
        else:
            # No explicit contract found - check for contextual operations on most recent position
            # Patterns: "De risking", "adding", "avg", "close the rest", "stopped out", etc.
            key, pos = _get_most_recent_active_position()

            if (
                any(keyword in alert.lower() for keyword in ["de risking", "derisk"])
                and pos
            ):
                # De-risking = partial trim on most recent active position
                current_status = pos["status"]
                # Treat as trim operation
                if current_status == "entry":
                    _update_position_status(
                        pos["ticker"],
                        pos["strike"],
                        pos["type"],
                        pos["expiry"],
                        "trim1",
                    )
                    alert = f"STC {pos['ticker']} {pos['strike']}{pos['type']} {pos['expiry']} @0 trim sold 45% (de-risk)"
                elif current_status == "trim1":
                    _update_position_status(
                        pos["ticker"],
                        pos["strike"],
                        pos["type"],
                        pos["expiry"],
                        "trim2",
                    )
                    alert = f"STC {pos['ticker']} {pos['strike']}{pos['type']} {pos['expiry']} @0 trim sold 45% (de-risk)"
                elif current_status == "trim2":
                    _update_position_status(
                        pos["ticker"],
                        pos["strike"],
                        pos["type"],
                        pos["expiry"],
                        "runners",
                    )
                    alert = f"ExitUpdate {pos['ticker']} {pos['strike']}{pos['type']} {pos['expiry']} runners (10% remain)"

            elif (
                any(
                    keyword in alert.lower()
                    for keyword in [
                        "close the rest",
                        "closing the rest",
                        "stopped out the rest",
                    ]
                )
                and pos
            ):
                # "Close the rest" = close remaining position (could be at any state)
                current_status = pos["status"]
                if current_status in ["trim1", "trim2", "runners"]:
                    # Close whatever remains
                    _update_position_status(
                        pos["ticker"],
                        pos["strike"],
                        pos["type"],
                        pos["expiry"],
                        "closed",
                    )
                    alert = f"STC {pos['ticker']} {pos['strike']}{pos['type']} {pos['expiry']} @0 close remaining"
                elif current_status == "entry":
                    # Full close without any trims
                    _update_position_status(
                        pos["ticker"],
                        pos["strike"],
                        pos["type"],
                        pos["expiry"],
                        "closed",
                    )
                    alert = f"STC {pos['ticker']} {pos['strike']}{pos['type']} {pos['expiry']} @0 full close"
            # Leave alert unchanged if can't determine operation
    else:
        # Check for contextual operations even without explicit Entry/Update/Exit markers
        # These are messages with just description: "Time to close the rest", "adding here", etc.
        alert_lower = alert.lower()

        # "close the rest" / "closing the rest" / "stopped out" patterns
        if any(
            phrase in alert_lower
            for phrase in [
                "close the rest",
                "closing the rest",
                "stopped out the rest",
                "stopped out",
            ]
        ):
            key, pos = _get_most_recent_active_position()
            if key and pos:
                current_status = pos["status"]
                # Close remaining position regardless of current state
                _update_position_status(
                    pos["ticker"],
                    pos["strike"],
                    pos["type"],
                    pos["expiry"],
                    "closed",
                )
                alert = f"STC {pos['ticker']} {pos['strike']}{pos['type']} {pos['expiry']} @0 close remaining"

        # "de risking" / "derisk" patterns - partial trim
        elif "de risk" in alert_lower or "derisk" in alert_lower:
            key, pos = _get_most_recent_active_position()
            if key and pos:
                current_status = pos["status"]
                if current_status == "entry":
                    # First trim: 45%
                    _update_position_status(
                        pos["ticker"],
                        pos["strike"],
                        pos["type"],
                        pos["expiry"],
                        "trim1",
                    )
                    alert = f"STC {pos['ticker']} {pos['strike']}{pos['type']} {pos['expiry']} @0 trim sold 45% (de-risk)"
                elif current_status == "trim1":
                    # Second trim: 45%
                    _update_position_status(
                        pos["ticker"],
                        pos["strike"],
                        pos["type"],
                        pos["expiry"],
                        "trim2",
                    )
                    alert = f"STC {pos['ticker']} {pos['strike']}{pos['type']} {pos['expiry']} @0 trim sold 45% (de-risk)"
                elif current_status == "trim2":
                    # Third+ trim: transition to runners (10% remain)
                    _update_position_status(
                        pos["ticker"],
                        pos["strike"],
                        pos["type"],
                        pos["expiry"],
                        "runners",
                    )
                    alert = f"ExitUpdate {pos['ticker']} {pos['strike']}{pos['type']} {pos['expiry']} runners (10% remain) (de-risk)"
                # else: already at runners or closed, leave as-is

        # "adding" patterns - position size increase (same size as original BTO)
        elif "adding" in alert_lower:
            # Handle follow-up add messages like "adding here mental stop under 501"
            key, pos = _get_most_recent_active_position()
            if key and pos:
                # Extract optional mental stop level
                ms_match = re.search(
                    r"mental stop (?:under|below)\s*(\d+(?:\.\d+)?)",
                    alert_lower,
                    re.IGNORECASE,
                )
                mental_stop = ms_match.group(1) if ms_match else None
                # Represent add as market add; price unknown at alert time
                alert = f"BTO {pos['ticker']} {pos['strike']}{pos['type'].upper()} {pos['expiry']} @ "
                if mental_stop:
                    # Append stop level in a parsable way (SL <level>) for downstream logic
                    alert += f" SL {mental_stop}"
        # Leave alert unchanged if no recognizable pattern

    message.content = alert
    return message


def rough_alerts(message_):
    """
    Reformat Discord message from rough to content message
    """
    if not message_.content:
        return message_

    message = MessageCopy(message_)
    pattern = r"\b(BTO)?\b(\d{1,2}\/\d{1,2})?\s*([A-Z]+)\s*(\d+[.\d+]*[c|p|C|P])\s*@\s*(\d+(?:[.]\d+)?|\.\d+)"
    match = re.search(pattern, message.content, re.IGNORECASE)
    if match:
        action, expDate, ticker, strike, price = match.groups()
        alert = f"BTO {ticker} {strike.upper()} {expDate} @{price}"
        message.content = alert
    return message


def format_alert_date_price(alert, possible_stock=False):
    alert = alert.replace("@everyone", "")
    pattern = r"\b(BTO|STC)?\b\s*(\d+)?\s*([A-Z]+)\s*(\d{1,2}\/\d{1,2})?(?:\/202\d|\/2\d)?(?:C|P)?\s*(\d+[.\d+]*[cp]?)?(?:\s*@\s*[$]*[ ]*(\d+(?:[,.]\d+)?|\.\d+))?"
    match = re.search(pattern, alert, re.IGNORECASE)
    if match:
        action, quantity, ticker, expDate, strike, price = match.groups()

        asset_type = "option" if strike and expDate else "stock"
        symbol = ticker.upper()
        price = f" @ {float(price.replace(',', '.'))}" if price else ""

        if asset_type == "option":
            # fix missing strike, assume Call
            if "c" not in strike.lower() and "p" not in strike.lower():
                strike = strike + "c"
            if action is None:  # assume BTO
                action = "BTO"
            alert = f"{action.upper()} {symbol} {strike.upper()} {expDate}{price}"
        elif asset_type == "stock" and possible_stock:
            alert = f"{action.upper()} {symbol}{price}"
    return alert


class MessageCopy:
    def __init__(self, original_message):
        self.created_at = original_message.created_at
        self.channel = ChannelCopy(original_message.channel)
        self.author = AuthorCopy(original_message.author)
        self.guild = GuildCopy(original_message.guild)
        self.embeds = [EmbedCopy(embed) for embed in original_message.embeds]
        self.content = original_message.content


class AuthorCopy:
    def __init__(self, original_author):
        self.name = original_author.name
        self.discriminator = original_author.discriminator
        self.id = original_author.id
        self.bot = original_author.bot


class ChannelCopy:
    def __init__(self, original_channel):
        self.id = original_channel.id


class GuildCopy:
    def __init__(self, original_guild):
        self.id = original_guild.id


class EmbedFieldCopy:
    def __init__(self, original_field):
        self.name = original_field.name
        self.value = original_field.value


class EmbedCopy:
    def __init__(self, original_embed):
        self.author = AuthorCopy(original_embed.author)
        self.title = original_embed.title
        self.description = original_embed.description
        self.fields = [EmbedFieldCopy(field) for field in original_embed.fields]

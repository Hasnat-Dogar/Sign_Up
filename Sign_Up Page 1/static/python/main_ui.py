# pyright: reportMissingImports=false
# pylint: disable=import-error
import re
from browser import document, timer , ajax

typing_timer = None
password_is_strong = False
debounce_timer = None


def handle_response(req):
    """Callback function triggered when Flask sends back the JSON data."""
    if req.status == 200 or req.status == 0:
        data = req.json
        message_element = document["username-message"]
        
        if data.get("status") == "empty":
            message_element.html = ""
            message_element.className = ""
            
        # FIX 1: Match the exact key from your Flask file -> data.get("Availibility")
        elif data.get("Availibility") is True:
            message_element.html = "✨ Awesome, that username is available!"
            message_element.className = "success-msg"
            
        else:
            message_element.html = "⚠️ Username already taken."
            message_element.className = "error-msg"
            
    else:
        print(f"Network error status received: {req.status}")

def trigger_api_fetch(user_name):
    """Sends a server-side request to your local Flask route with clean parameters."""
    
    # 1. Package your input into a data dictionary. 
    # Brython will automatically sanitize and format this into the URL string.
    params = {"user_name": user_name}
    
    # 2. Pass the dictionary directly into ajax.get using the 'data' parameter argument
    ajax.get(
        "/api/check-username", 
        data=params, 
        mode="json", 
        oncomplete=handle_response
    )


def on_username_input(event):
    """Triggered on every keystroke to manage the debounce mechanism."""
    global debounce_timer
    
    user_name = event.target.value.strip()
    
    if debounce_timer is not None:
        timer.clear_timeout(debounce_timer)
        
    debounce_timer = timer.set_timeout(lambda: trigger_api_fetch(user_name), 500)


try:
    # FIX 2: Match your HTML input ID -> "user_name" (with an underscore)
    document["user_name"].bind("input", on_username_input)
except KeyError:
    pass


def toggle_password(event):
        password1 = document["password"]
        icon1 = document["password-icon"]
        
        if password1.type == "password":
            password1.type = "text"
            icon1.innerHTML = "🔓"
        else:
            password1.type = "password"
            icon1.innerHTML = "🔒"


def toggle_confirm_password(event):
        password2 = document["c_password"]
        icon2 = document["confirm-icon"]
        
        if password2.type == "password":
            password2.type = "text"
            icon2.innerHTML = "🔓"
        else:
            password2.type = "password"
            icon2.innerHTML = "🔒"


def toggle_login_pass(event):
        login_password = document["login_password"]
        login_icon = document["login-pass-icon"]
        if login_password.type == "password":
            login_password.type = "text"
            login_icon.innerHTML = "🔓"
        else:
            login_password.type = "password"
            login_icon.innerHTML = "🔒"


def clear_shake_effects():
    try:
        document["password"].classList.remove("shake-field")
        document["c_password"].classList.remove("shake-field")
    except KeyError:
        pass


def check_password_strength(event):
    global password_is_strong
    
    try:
        password_val = document["password"].value
        p1 = document["password"]
        p2 = document["c_password"]
        match_error = document["same_pass_error"]
        heading1 = document["pass-label"]
        heading2 = document["weak-pass-label"]
        req_list = document["password-requirements"]
        button = document["submit-button"]
        
        has_min_length = len(password_val) >= 8
        has_number = re.search(r"\d", password_val) is not None
        has_uppercase = re.search(r"[A-Z]", password_val) is not None
        
        if has_min_length and has_number and has_uppercase:
            password_is_strong = True
            req_list.style.opacity = "0"
            timer.set_timeout(lambda: setattr(req_list.style, "display", "none"), 300)
            heading1.style.display = "contents"
            heading1.style.color = "#4cd137"
            heading2.style.display = "none"
            
            if p2.value is not None:
                validate_passwords()
        else:
            button.disabled = True
            password_is_strong = False
            match_error.style.display = 'none'
            p1.style.border = p2.style.border = "1px solid rgba(255, 255, 255, 0.12)"
            p1.style.outline = p2.style.outline = "2px solid transparent"
            clear_shake_effects()
            
            if len(password_val) > 0:
                req_list.style.display = "block"
                heading1.style.display = "none"
                heading2.style.display = "contents"
                heading2.style.color = "red"
                timer.set_timeout(lambda: setattr(req_list.style, "opacity", "1"), 10)
            else:
                req_list.style.opacity = "0"
                heading2.style.display = "none"
                timer.set_timeout(lambda: setattr(req_list.style, "display", "none"), 300)
                
        req_len = document["req-length"]
        req_len.style.color = "#4cd137" if has_min_length else "#888"
        req_len.innerHTML = "✓ Minimum 8 characters" if has_min_length else "✕ Minimum 8 characters"
        
        req_num = document["req-number"]
        req_num.style.color = "#4cd137" if has_number else "#888"
        req_num.innerHTML = "✓ At least 1 number" if has_number else "✕ At least 1 number"
        
        req_up = document["req-uppercase"]
        req_up.style.color = "#4cd137" if has_uppercase else "#888"
        req_up.innerHTML = "✓ At least 1 uppercase letter" if has_uppercase else "✕ At least 1 uppercase letter"
        
    except KeyError:
        pass


def validate_passwords():
    global password_is_strong
    
    try:
        password1 = document["password"]
        password2 = document["c_password"]
        match_error = document["same_pass_error"]
        
        if not password_is_strong:
            match_error.style.display = 'none'
            return
            
        if password1.value == "" or password2.value == "":
            match_error.style.display = 'none'
            password1.style.border = password2.style.border = "1px solid rgba(255, 255, 255, 0.12)"
            password1.style.outline = password2.style.outline = "2px solid transparent"
            
        elif password1.value == password2.value:
            match_error.style.display = 'none'
            password1.style.border = password2.style.border = "1px solid #4cd137"
            password1.style.outline = password2.style.outline = "2px solid #4cd137"
            
        else:
            password1.style.border = password2.style.border = "1px solid #ff4d4d"
            password1.style.outline = password2.style.outline = "2px solid #ff4d4d"
            match_error.style.display = 'block'
            
            password1.classList.remove("shake-field")
            password2.classList.remove("shake-field")
            timer.set_timeout(lambda: password1.classList.add("shake-field"), 10)
            timer.set_timeout(lambda: password2.classList.add("shake-field"), 10)
            timer.set_timeout(clear_shake_effects, 400)
    except KeyError:
        pass


def check_pass(event):
    global typing_timer
    if typing_timer is not None:
        timer.clear_timeout(typing_timer)
    typing_timer = timer.set_timeout(validate_passwords, 600)



try:
    document["password-toggle"].bind("click", toggle_password)
except KeyError:
    pass

try:
    document["confirm-toggle"].bind("click", toggle_confirm_password)
except KeyError:
    pass

try:
    document["login-pass-toggle"].bind("click", toggle_login_pass)
except KeyError:
    pass

try:
    document["password"].bind("input", check_password_strength)
    document["password"].bind("input", check_pass)
    document["c_password"].bind("input", check_pass)
except KeyError:
    pass

# pyright: reportMissingImports=false
# pylint: disable=import-error
import re
from browser import document, timer

typing_timer = None
password_is_strong = False

def toggle_password(event):
    p1 = document["password"]
    p2 = document["c_password"]
    icon1 = document["password-icon"]
    icon2 = document["confirm-icon"]
    
    if p1.type == "password":
        p1.type = p2.type = "text"
        icon1.innerHTML = icon2.innerHTML = "🔓"
    else:
        p1.type = p2.type = "password"
        icon1.innerHTML = icon2.innerHTML = "🔒"

def toggle_confirm(event):
    p1 = document["password"]
    p2 = document["c_password"]
    icon1 = document["password-icon"]
    icon2 = document["confirm-icon"]
    
    if p2.type == "password":
        p1.type = p2.type = "text"
        icon1.innerHTML = icon2.innerHTML = "🔓"
    else:
        p1.type = p2.type = "password"
        icon1.innerHTML = icon2.innerHTML = "🔒"

def toggle_login_pass(event):
    input_field = document["login_password"]
    icon = document["login-pass-icon"]
    if input_field.type == "password":
        input_field.type = "text"
        icon.innerHTML = "🔓"
    else:
        input_field.type = "password"
        icon.innerHTML = "🔒"

def clear_shake_effects():
    try:
        document["password"].classList.remove("shake-field")
        document["c_password"].classList.remove("shake-field")
    except KeyError:
        pass

def check_password_strength(event):
    global password_is_strong
    
    password_val = document["password"].value
    p1 = document["password"]
    p2 = document["c_password"]
    match_error = document["same_pass_error"]
    
    try:
        req_list = document["password-requirements"]
        
        has_min_length = len(password_val) >= 8
        has_number = re.search(r"\d", password_val) is not None
        has_uppercase = re.search(r"[A-Z]", password_val) is not None
        
        if has_min_length and has_number and has_uppercase:
            password_is_strong = True
            req_list.style.opacity = "0"
            timer.set_timeout(lambda: setattr(req_list.style, "display", "none"), 300)
            
            if p2.value != "":
                validate_passwords()
        else:
            password_is_strong = False
            match_error.style.display = 'none'
            p1.style.border = p2.style.border = "1px solid rgba(255, 255, 255, 0.12)"
            p1.style.outline = p2.style.outline = "2px solid transparent"
            clear_shake_effects()
            
            if len(password_val) > 0:
                req_list.style.display = "block"
                timer.set_timeout(lambda: setattr(req_list.style, "opacity", "1"), 10)
            else:
                req_list.style.opacity = "0"
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
    
    password1 = document["password"]
    password2 = document["c_password"]
    match_error = document["same_pass_error"]
    
    clear_shake_effects()
    
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
        
        password1.classList.add("shake-field")
        password2.classList.add("shake-field")
        timer.set_timeout(clear_shake_effects, 400)

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
    document["confirm-toggle"].bind("click", toggle_confirm)
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

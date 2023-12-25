export async function bodyRequest(url, body, headers = {}, method = 'POST', autoContentType=false, file=false) {
    let additional_headers;
    if (!autoContentType) {
        additional_headers = {
            'Content-Type': 'application/json',
        }
    } else {
        additional_headers = {}
    }
    for (const [key, value] of Object.entries(headers)) {
        additional_headers[key] = value;
    }
    return await fetch(url, {
        method: method,
        headers: additional_headers,
        body: !file ? JSON.stringify(body) : body
    })
}

export async function getRequest(url, headers = {}) {
    const additional_headers = {
        'Content-Type': 'application/json',
    }
    for (const [key, value] of Object.entries(headers)) {
        additional_headers[key] = value
    }
    return await fetch(url, {
        method: "GET",
        headers: additional_headers,
    })
}


export async function deleteRequest(url, headers = {}) {
    const additional_headers = {
        'Content-Type': 'application/json',
    }
    for (const [key, value] of Object.entries(headers)) {
        additional_headers[key] = value
    }
    return await fetch(url, {
        method: "DELETE",
        headers: additional_headers,
    })
}


async function refreshToken(refresh_token) {
    const body = {
        "refresh_token": refresh_token
    }
    const refresh_response = await bodyRequest('/auth/token/refresh', body)
    if (refresh_response.status === 401) {
        document.cookie = "email=" + "" + "; SameSite=strict" + "; max-age=" + 0;
        throw "noAuth";
    }
    if (refresh_response.status === 200) {
        const data = await refresh_response.json()
        localStorage.setItem("access_token", data.access_token)
        return data.access_token
    }
}


export async function getRequestWithAuth(url) {
    const access_token = localStorage.getItem('access_token');
    const refresh_token = localStorage.getItem('refresh_token');
    if (access_token === null || refresh_token === null) {
        document.cookie = "email=" + "" + "; SameSite=strict" + "; max-age=" + 0;
        throw 'noAuth';
    }
    const response = await getRequest(url, {'Authorization': 'Bearer ' + access_token});
    if (response.status === 401) {
        const new_access_token = await refreshToken(refresh_token)
        const second_response = await getRequest(url, {'Authorization': 'Bearer ' + new_access_token});
        if (second_response.status !== 401) {
            return second_response
        } else {
            document.cookie = "email=" + "" + "; SameSite=strict" + "; max-age=" + 0;
            throw "noAuth"
        }
    }
    return response
}


export async function deleteRequestWithAuth(url) {
    const access_token = localStorage.getItem('access_token');
    const refresh_token = localStorage.getItem('refresh_token');
    if (access_token === null || refresh_token === null) {
        document.cookie = "email=" + "" + "; SameSite=strict" + "; max-age=" + 0;
        throw 'noAuth'
    }
    const response = await deleteRequest(url, {'Authorization': 'Bearer ' + access_token});
    if (response.status === 401) {
        const new_access_token = await refreshToken(refresh_token)
        const second_response = await deleteRequest(url, {'Authorization': 'Bearer ' + new_access_token});
        if (second_response.status !== 401) {
            return second_response
        } else {
            document.cookie = "email=" + "" + "; SameSite=strict" + "; max-age=" + 0;
            throw "noAuth"
        }
    }
    return response
}


export async function bodyRequestWithAuth(url, body, method = "POST", autoContentType=false, file=false) {
    const access_token = localStorage.getItem('access_token');
    const refresh_token = localStorage.getItem('refresh_token');
    if (access_token === null || refresh_token === null) {
        document.cookie = "email=" + "" + "; SameSite=strict" + "; max-age=" + 0;
        throw 'noAuth'
    }
    const response = await bodyRequest(url, body, {
        'Authorization': 'Bearer ' + access_token,
    }, method, autoContentType, file);
    if (response.status === 401) {
        const new_access_token = await refreshToken(refresh_token)
        const second_response = await bodyRequest(url, body, {
            'Authorization': 'Bearer ' + new_access_token,
        }, method, autoContentType, file);
        if (second_response.status !== 401) {
            return second_response
        } else {
            document.cookie = "email=" + "" + "; SameSite=strict" + "; max-age=" + 0;
            throw "noAuth"
        }
    }
    return response
}

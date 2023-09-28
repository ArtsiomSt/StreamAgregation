async function postRequest(url, body, headers = {}){
    const additional_headers = {
        'Content-Type': 'application/json',
    }
    for (const [key, value] of Object.entries(headers)){
        additional_headers[key] = value
    }
    return await fetch(url, {
        method: "POST",
        headers: additional_headers,
        body: JSON.stringify(body)
    })
}

async function getRequest(url, headers = {}){
    const additional_headers = {
        'Content-Type': 'application/json',
    }
    for (const [key, value] of Object.entries(headers)){
        additional_headers[key] = value
    }
    return await fetch(url, {
        method: "GET",
        headers: additional_headers,
    })
}

async function refreshToken(refresh_token){
    const body = {
        "refresh_token": refresh_token
    }
    const refresh_response = await postRequest('/auth/token/refresh', body)
    if (refresh_response.status === 401){
        throw "badAuth"
    }
    if (refresh_response.status === 200){
        const data = await refresh_response.json()
        localStorage.setItem("access_token", data.access_token)
        return data.access_token
    }
}

export async function getRequestWithAuth(url){
    const access_token = localStorage.getItem('access_token');
    const refresh_token = localStorage.getItem('refresh_token');
    if (access_token === null || refresh_token === null){
        throw 'noAuth'
    }
    const response = await getRequest(url, {'Authorization': 'Bearer ' + access_token});
    if (response.status === 401){
        const new_access_token = await refreshToken(refresh_token)
        const second_response = await getRequest(url, {'Authorization': 'Bearer ' + new_access_token});
        if (second_response.status === 200){
            return second_response
        }
        else{
            throw "noAuth"
        }
    }
    if (response.status === 200){
        return response
    }
}


export async function postRequestWithAuth(url, body){
    const access_token = localStorage.getItem('access_token');
    const refresh_token = localStorage.getItem('refresh_token');
    if (access_token === null || refresh_token === null){
        throw 'noAuth'
    }
    const response = await postRequest(url, body, {'Authorization': 'Bearer ' + access_token});
    if (response.status === 401){
        const new_access_token = await refreshToken(refresh_token)
        const second_response = await postRequest(url, body, {'Authorization': 'Bearer ' + new_access_token});
        if (second_response.status === 200){
            return second_response
        }
        else{
            throw "noAuth"
        }
    }
    if (response.status === 200){
        return response
    }
}

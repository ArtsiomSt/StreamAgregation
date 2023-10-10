export function getCookie(name) {
  const cookies = document.cookie.split(';').map(cookie => cookie.trim().split('='));
  const cookie = cookies.find(cookie => cookie[0] === name);
  return cookie ? cookie[1] : undefined;
}

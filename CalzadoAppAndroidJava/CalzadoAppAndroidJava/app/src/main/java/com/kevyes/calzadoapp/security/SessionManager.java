package com.kevyes.calzadoapp.security;

import android.content.Context;
import android.content.SharedPreferences;

public class SessionManager {
    private static final String PREFS = "calzado_session";
    private static final String TOKEN = "token";
    private static final String USER_ID = "user_id";
    private static final String NAME = "name";
    private static final String ROLE = "role";
    private final SharedPreferences prefs;

    public SessionManager(Context context) {
        prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    public void login(long userId, String name, String role) {
        long expiration = System.currentTimeMillis() + 60 * 60 * 1000L;
        String token = DemoJwtService.createToken(String.valueOf(userId), role, expiration);
        prefs.edit()
                .putString(TOKEN, token)
                .putLong(USER_ID, userId)
                .putString(NAME, name)
                .putString(ROLE, role)
                .apply();
    }

    public boolean isLoggedIn() {
        String token = prefs.getString(TOKEN, null);
        return token != null && DemoJwtService.isValid(token);
    }

    public long getUserId() { return prefs.getLong(USER_ID, -1); }
    public String getName() { return prefs.getString(NAME, ""); }
    public String getRole() { return prefs.getString(ROLE, ""); }

    public void logout() { prefs.edit().clear().apply(); }
}

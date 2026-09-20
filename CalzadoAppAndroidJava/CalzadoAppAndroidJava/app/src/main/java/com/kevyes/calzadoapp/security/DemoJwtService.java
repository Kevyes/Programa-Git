package com.kevyes.calzadoapp.security;

import android.util.Base64;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;

public final class DemoJwtService {
    private static final String SECRET = "CALZADO-APP-DEMO-SECRET-2026";

    private DemoJwtService() { }

    public static String createToken(String subject, String role, long expirationMillis) {
        String header = base64Url("{\"alg\":\"HS256\",\"typ\":\"JWT\"}");
        String payload = base64Url("{\"sub\":\"" + subject + "\",\"role\":\"" + role + "\",\"exp\":" + expirationMillis + "}");
        String content = header + "." + payload;
        return content + "." + sign(content);
    }

    public static boolean isValid(String token) {
        try {
            String[] parts = token.split("\\.");
            if (parts.length != 3) return false;
            String expected = sign(parts[0] + "." + parts[1]);
            if (!expected.equals(parts[2])) return false;
            String payload = new String(Base64.decode(parts[1], Base64.URL_SAFE | Base64.NO_WRAP), StandardCharsets.UTF_8);
            String marker = "\"exp\":";
            int start = payload.indexOf(marker);
            if (start < 0) return false;
            start += marker.length();
            int end = payload.indexOf('}', start);
            long exp = Long.parseLong(payload.substring(start, end));
            return System.currentTimeMillis() < exp;
        } catch (Exception e) {
            return false;
        }
    }

    private static String sign(String value) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(SECRET.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
            return Base64.encodeToString(mac.doFinal(value.getBytes(StandardCharsets.UTF_8)), Base64.URL_SAFE | Base64.NO_WRAP | Base64.NO_PADDING);
        } catch (Exception e) {
            throw new IllegalStateException("No se pudo firmar el token.", e);
        }
    }

    private static String base64Url(String value) {
        return Base64.encodeToString(value.getBytes(StandardCharsets.UTF_8), Base64.URL_SAFE | Base64.NO_WRAP | Base64.NO_PADDING);
    }
}

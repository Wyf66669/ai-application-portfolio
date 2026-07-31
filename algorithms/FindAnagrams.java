import java.util.*;

/** 438. 找到字符串中所有字母异位词 — 固定窗口 + 26 位频次数组 */
class FindAnagrams {
    public List<Integer> findAnagrams(String s, String p) {
        List<Integer> result = new ArrayList<>();
        if (s.length() < p.length()) {
            return result;
        }
        int[] pCount = new int[26];
        int[] sCount = new int[26];
        for (char c : p.toCharArray()) {
            pCount[c - 'a']++;
        }
        int left = 0;
        int right = 0;
        while (right < s.length()) {
            sCount[s.charAt(right) - 'a']++;
            right++;
            if (right - left > p.length()) {
                sCount[s.charAt(left) - 'a']--;
                left++;
            }
            if (right - left == p.length() && Arrays.equals(sCount, pCount)) {
                result.add(left);
            }
        }
        return result;
    }
}

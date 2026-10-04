package jp.sales.target;

import android.content.Context;
import android.database.Cursor;
import android.net.Uri;
import android.provider.OpenableColumns;

import org.json.JSONArray;
import org.json.JSONObject;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

import javax.xml.parsers.DocumentBuilderFactory;

public final class DataProcessor {
    private static final String CAT_CARD = "段ボール";
    private static final String CAT_GOODS = "商品";
    private static final String CAT_PLATE = "判型";
    private static final List<String> CATS = Arrays.asList(CAT_CARD, CAT_GOODS, CAT_PLATE);
    private static final Charset CSV_CHARSET = Charset.forName("MS932");
    private static final Pattern REP_IN_FILENAME = Pattern.compile("年度\\s*([0-9]+)", Pattern.CASE_INSENSITIVE);
    private static final Pattern TRAILING_NUMBER = Pattern.compile("([0-9]+)(?=\\.(?:xlsm|xlsx)$)", Pattern.CASE_INSENSITIVE);

    private DataProcessor() {}

    public static String process(Context context, List<Uri> goalUris, Uri salesUri, Uri masterUri) throws Exception {
        if (goalUris == null || goalUris.isEmpty()) throw new IllegalArgumentException("販売目標表が選択されていません");

        GoalData goal = new GoalData();
        int fallbackRep = 1;
        List<String> goalNames = new ArrayList<>();
        for (Uri goalUri : goalUris) {
            String fileName = displayName(context, goalUri);
            goalNames.add(fileName);
            String repId = inferSalespersonId(fileName, fallbackRep++);
            GoalData one = parseGoalWorkbook(context, goalUri, repId);
            mergeGoal(goal, one);
        }
        if (goal.customers.isEmpty()) throw new IllegalArgumentException("得意先シートを読み取れませんでした");
        if (goal.year == 0) goal.year = 2026;

        CatSet allTarget = sumSets(goal.targets, false);
        LinkedHashMap<String, CatSet> reorderedTargets = new LinkedHashMap<>();
        reorderedTargets.put("ALL", allTarget);
        reorderedTargets.putAll(goal.targets);
        goal.targets.clear();
        goal.targets.putAll(reorderedTargets);

        Map<String, Double> sqmLookup = parseMaster(context, masterUri);
        ActualResult actual = parseSales(context, salesUri, sqmLookup, goal);

        JSONObject root = new JSONObject();
        root.put("year", goal.year);
        JSONArray months = new JSONArray();
        for (int m = 4; m <= 9; m++) months.put(m + "月");
        root.put("months", months);

        JSONArray salespeople = new JSONArray();
        JSONObject allRep = new JSONObject();
        allRep.put("id", "ALL");
        allRep.put("name", "全営業");
        salespeople.put(allRep);
        for (String repId : goal.salespeople.keySet()) {
            JSONObject o = new JSONObject();
            o.put("id", repId);
            o.put("name", "営業 " + repId);
            salespeople.put(o);
        }
        root.put("salespeople", salespeople);

        JSONArray customers = new JSONArray();
        customers.put(customerJson("ALL", "全体", "ALL"));
        for (Map.Entry<String, String> e : goal.customers.entrySet()) {
            String repId = goal.customerSalesperson.get(e.getKey());
            customers.put(customerJson(e.getKey(), e.getValue(), repId == null ? "" : repId));
        }
        root.put("customers", customers);
        root.put("targets", setsToJson(goal.targets));
        root.put("actuals", setsToJson(actual.actuals));

        JSONObject meta = new JSONObject();
        meta.put("goalFile", String.join(" / ", goalNames));
        meta.put("goalCount", goalNames.size());
        meta.put("salesFile", displayName(context, salesUri));
        meta.put("masterFile", displayName(context, masterUri));
        meta.put("sqmJoinHits", actual.joinHits);
        meta.put("sqmJoinMisses", actual.joinMisses);
        root.put("meta", meta);
        return root.toString();
    }

    private static JSONObject customerJson(String id, String name, String repId) throws Exception {
        JSONObject o = new JSONObject();
        o.put("id", id);
        o.put("name", name == null || name.isEmpty() ? id : name);
        o.put("salesperson", repId == null ? "" : repId);
        return o;
    }

    private static JSONObject setsToJson(Map<String, CatSet> src) throws Exception {
        JSONObject out = new JSONObject();
        for (Map.Entry<String, CatSet> e : src.entrySet()) {
            JSONObject cats = new JSONObject();
            for (String cat : CATS) {
                Metrics m = e.getValue().byCat.get(cat);
                if (m == null) m = new Metrics();
                JSONObject mo = new JSONObject();
                mo.put("amount", arrayJson(m.amount));
                mo.put("sqm", arrayJson(m.sqm));
                cats.put(cat, mo);
            }
            out.put(e.getKey(), cats);
        }
        return out;
    }

    private static JSONArray arrayJson(double[] arr) throws Exception {
        JSONArray a = new JSONArray();
        for (double v : arr) a.put(round(v, 6));
        return a;
    }

    private static double round(double v, int places) {
        double p = Math.pow(10, places);
        return Math.round(v * p) / p;
    }

    private static final class Metrics {
        final double[] amount = new double[6];
        final double[] sqm = new double[6];
    }

    private static final class CatSet {
        final Map<String, Metrics> byCat = new LinkedHashMap<>();
        CatSet() {
            for (String c : CATS) byCat.put(c, new Metrics());
        }
    }

    private static final class GoalData {
        int year = 0;
        final LinkedHashMap<String, String> salespeople = new LinkedHashMap<>();
        final LinkedHashMap<String, String> customers = new LinkedHashMap<>();
        final LinkedHashMap<String, String> customerSalesperson = new LinkedHashMap<>();
        final LinkedHashMap<String, CatSet> targets = new LinkedHashMap<>();
    }

    private static final class ActualResult {
        final LinkedHashMap<String, CatSet> actuals = new LinkedHashMap<>();
        int joinHits = 0;
        int joinMisses = 0;
    }

    private static void mergeGoal(GoalData dst, GoalData src) {
        if (dst.year == 0) dst.year = src.year;
        else if (src.year != 0 && dst.year != src.year) {
            throw new IllegalArgumentException("販売目標表の年度が一致していません: " + dst.year + " / " + src.year);
        }
        dst.salespeople.putAll(src.salespeople);
        for (Map.Entry<String, String> e : src.customers.entrySet()) {
            String id = e.getKey();
            if (dst.customers.containsKey(id)) {
                String oldRep = dst.customerSalesperson.get(id);
                String newRep = src.customerSalesperson.get(id);
                if (oldRep == null || !oldRep.equals(newRep)) {
                    throw new IllegalArgumentException("請求先 " + id + " が複数の担当営業に登録されています");
                }
            }
            dst.customers.put(id, e.getValue());
            dst.customerSalesperson.put(id, src.customerSalesperson.get(id));
            dst.targets.put(id, src.targets.get(id));
        }
    }

    private static GoalData parseGoalWorkbook(Context context, Uri uri, String defaultRepId) throws Exception {
        Map<String, byte[]> zip = new HashMap<>();
        try (InputStream in = context.getContentResolver().openInputStream(uri);
             ZipInputStream zin = new ZipInputStream(in)) {
            ZipEntry e;
            byte[] buf = new byte[16384];
            while ((e = zin.getNextEntry()) != null) {
                String name = e.getName();
                if (name.equals("xl/workbook.xml") || name.equals("xl/_rels/workbook.xml.rels") ||
                        name.equals("xl/sharedStrings.xml") || name.startsWith("xl/worksheets/")) {
                    ByteArrayOutputStream bos = new ByteArrayOutputStream();
                    int n;
                    while ((n = zin.read(buf)) > 0) bos.write(buf, 0, n);
                    zip.put(name, bos.toByteArray());
                }
                zin.closeEntry();
            }
        }
        if (!zip.containsKey("xl/workbook.xml")) throw new IllegalArgumentException("販売目標表のworkbook.xmlが見つかりません");

        List<String> shared = parseSharedStrings(zip.get("xl/sharedStrings.xml"));
        Map<String, String> rels = parseWorkbookRels(zip.get("xl/_rels/workbook.xml.rels"));
        Document workbook = parseXml(zip.get("xl/workbook.xml"));
        NodeList sheets = workbook.getElementsByTagName("sheet");

        GoalData out = new GoalData();
        for (int i = 0; i < sheets.getLength(); i++) {
            Element se = (Element) sheets.item(i);
            String sheetName = se.getAttribute("name");
            String rid = se.getAttribute("r:id");
            if (rid == null || rid.isEmpty()) rid = se.getAttribute("id");
            String target = rels.get(rid);
            if (target == null) continue;
            String path = target.startsWith("/") ? target.substring(1) : target;
            if (!path.startsWith("xl/")) path = "xl/" + path;
            path = normalizePath(path);
            byte[] sheetBytes = zip.get(path);
            if (sheetBytes == null) continue;
            Map<String, String> cells = parseSheetCells(sheetBytes, shared);

            if (out.year == 0) {
                int y = (int) parseDouble(cells.get("B2"));
                if (y == 0) y = (int) parseDouble(cells.get("B1"));
                if (y >= 2000 && y <= 2200) out.year = y;
            }
            if ("全体".equals(sheetName)) continue;

            String id = norm(cells.get("B3"));
            if (id.isEmpty()) id = norm(sheetName);
            if (!id.matches("\\d+")) continue;
            String name = safe(cells.get("C3"));
            if (name.isEmpty()) name = id;
            String repId = detectSalespersonFromCells(cells);
            if (repId.isEmpty()) repId = defaultRepId;

            out.salespeople.put(repId, repId);
            out.customers.put(id, name);
            out.customerSalesperson.put(id, repId);
            CatSet set = new CatSet();
            readGoalRow(cells, 10, set.byCat.get(CAT_CARD).amount, 1000.0);
            readGoalRow(cells, 8, set.byCat.get(CAT_CARD).sqm, 1000.0);
            readGoalRow(cells, 17, set.byCat.get(CAT_GOODS).amount, 1000.0);
            readGoalRow(cells, 24, set.byCat.get(CAT_PLATE).amount, 1000.0);
            out.targets.put(id, set);
        }

        if (out.customers.isEmpty()) throw new IllegalArgumentException("販売目標表に得意先シートがありません");
        if (out.year == 0) out.year = 2026;
        return out;
    }

    private static String detectSalespersonFromCells(Map<String, String> cells) {
        for (int r = 1; r <= 12; r++) {
            for (char c = 'A'; c <= 'H'; c++) {
                String ref = String.valueOf(c) + r;
                String v = safe(cells.get(ref)).replace(" ", "").replace("　", "");
                if (v.contains("担当営業") || v.contains("営業担当") || v.contains("営業番号") || v.contains("担当者番号")) {
                    for (int dc = 1; dc <= 2; dc++) {
                        char cc = (char) (c + dc);
                        String n = norm(cells.get(String.valueOf(cc) + r));
                        if (n.matches("\\d+")) return n;
                    }
                }
            }
        }
        return "";
    }

    private static String inferSalespersonId(String fileName, int fallback) {
        String name = fileName == null ? "" : fileName;
        Matcher m = REP_IN_FILENAME.matcher(name);
        if (m.find()) return stripLeadingZeros(m.group(1));
        m = TRAILING_NUMBER.matcher(name);
        if (m.find()) return stripLeadingZeros(m.group(1));
        return String.valueOf(fallback);
    }

    private static String stripLeadingZeros(String s) {
        if (s == null || s.isEmpty()) return s;
        try { return String.valueOf(Long.parseLong(s)); }
        catch (Exception e) { return s; }
    }

    private static String normalizePath(String p) {
        while (p.contains("../")) {
            int i = p.indexOf("../");
            int slash = p.lastIndexOf('/', Math.max(0, i - 2));
            if (slash < 0) p = p.substring(i + 3);
            else p = p.substring(0, slash + 1) + p.substring(i + 3);
        }
        return p.replace("/./", "/");
    }

    private static void readGoalRow(Map<String, String> cells, int row, double[] dst, double multiplier) {
        for (int i = 0; i < 6; i++) {
            char col = (char) ('C' + i);
            dst[i] = parseDouble(cells.get(String.valueOf(col) + row)) * multiplier;
        }
    }

    private static CatSet sumSets(Map<String, CatSet> sets, boolean includeAll) {
        CatSet all = new CatSet();
        for (Map.Entry<String, CatSet> e : sets.entrySet()) {
            if (!includeAll && "ALL".equals(e.getKey())) continue;
            for (String cat : CATS) {
                Metrics src = e.getValue().byCat.get(cat);
                Metrics dst = all.byCat.get(cat);
                for (int i = 0; i < 6; i++) {
                    dst.amount[i] += src.amount[i];
                    dst.sqm[i] += src.sqm[i];
                }
            }
        }
        return all;
    }

    private static List<String> parseSharedStrings(byte[] bytes) throws Exception {
        List<String> out = new ArrayList<>();
        if (bytes == null) return out;
        Document doc = parseXml(bytes);
        NodeList sis = doc.getElementsByTagName("si");
        for (int i = 0; i < sis.getLength(); i++) {
            Element si = (Element) sis.item(i);
            NodeList ts = si.getElementsByTagName("t");
            StringBuilder sb = new StringBuilder();
            for (int j = 0; j < ts.getLength(); j++) sb.append(ts.item(j).getTextContent());
            out.add(sb.toString());
        }
        return out;
    }

    private static Map<String, String> parseWorkbookRels(byte[] bytes) throws Exception {
        Map<String, String> out = new HashMap<>();
        if (bytes == null) return out;
        Document doc = parseXml(bytes);
        NodeList rs = doc.getElementsByTagName("Relationship");
        for (int i = 0; i < rs.getLength(); i++) {
            Element e = (Element) rs.item(i);
            out.put(e.getAttribute("Id"), e.getAttribute("Target"));
        }
        return out;
    }

    private static Map<String, String> parseSheetCells(byte[] bytes, List<String> shared) throws Exception {
        Map<String, String> out = new HashMap<>();
        Document doc = parseXml(bytes);
        NodeList cs = doc.getElementsByTagName("c");
        for (int i = 0; i < cs.getLength(); i++) {
            Element c = (Element) cs.item(i);
            String ref = c.getAttribute("r");
            if (ref == null || ref.isEmpty()) continue;
            String type = c.getAttribute("t");
            String value = "";
            if ("inlineStr".equals(type)) {
                NodeList ts = c.getElementsByTagName("t");
                StringBuilder sb = new StringBuilder();
                for (int j = 0; j < ts.getLength(); j++) sb.append(ts.item(j).getTextContent());
                value = sb.toString();
            } else {
                NodeList vs = c.getElementsByTagName("v");
                if (vs.getLength() > 0) value = vs.item(0).getTextContent();
                if ("s".equals(type) && !value.isEmpty()) {
                    int idx = (int) parseDouble(value);
                    if (idx >= 0 && idx < shared.size()) value = shared.get(idx);
                }
            }
            out.put(ref, value);
        }
        return out;
    }

    private static Document parseXml(byte[] bytes) throws Exception {
        DocumentBuilderFactory f = DocumentBuilderFactory.newInstance();
        f.setNamespaceAware(false);
        try { f.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true); } catch (Exception ignored) {}
        try { f.setFeature("http://xml.org/sax/features/external-general-entities", false); } catch (Exception ignored) {}
        try { f.setFeature("http://xml.org/sax/features/external-parameter-entities", false); } catch (Exception ignored) {}
        return f.newDocumentBuilder().parse(new ByteArrayInputStream(bytes));
    }

    private static Map<String, Double> parseMaster(Context context, Uri uri) throws Exception {
        Map<String, Double> map = new HashMap<>(20000);
        try (InputStream in = context.getContentResolver().openInputStream(uri);
             BufferedReader br = new BufferedReader(new InputStreamReader(in, CSV_CHARSET), 65536)) {
            String headerLine = br.readLine();
            if (headerLine == null) throw new IllegalArgumentException("商品台帳CSVが空です");
            List<String> header = parseCsvLine(stripBom(headerLine));
            Map<String, Integer> idx = headerIndex(header);
            int iCustomer = required(idx, "請求先番号");
            int iProduct = required(idx, "商品番号");
            int iPart = required(idx, "付属番号");
            int iSqm = required(idx, "売上平米");
            String line;
            while ((line = br.readLine()) != null) {
                if (line.isEmpty()) continue;
                List<String> row = parseCsvLine(line);
                if (row.size() <= Math.max(Math.max(iCustomer, iProduct), Math.max(iPart, iSqm))) continue;
                String key = key(norm(row.get(iCustomer)), norm(row.get(iProduct)), norm(row.get(iPart)));
                double sqm = parseDouble(row.get(iSqm));
                if (!key.startsWith("||")) map.put(key, sqm);
            }
        }
        return map;
    }

    private static ActualResult parseSales(Context context, Uri uri, Map<String, Double> sqmLookup, GoalData goal) throws Exception {
        ActualResult out = new ActualResult();
        Set<String> targetIds = new HashSet<>();
        for (String id : goal.customers.keySet()) {
            targetIds.add(id);
            out.actuals.put(id, new CatSet());
        }

        try (InputStream in = context.getContentResolver().openInputStream(uri);
             BufferedReader br = new BufferedReader(new InputStreamReader(in, CSV_CHARSET), 65536)) {
            String headerLine = br.readLine();
            if (headerLine == null) throw new IllegalArgumentException("実績CSVが空です");
            List<String> header = parseCsvLine(stripBom(headerLine));
            Map<String, Integer> idx = headerIndex(header);
            int iDate = required(idx, "売上日", "売上日付");
            int iClass = required(idx, "商品分類名");
            int iCustomer = required(idx, "請求先番号");
            int iProduct = required(idx, "商品番号");
            int iPart = required(idx, "付属番号");
            int iQty = required(idx, "売上数量");
            int iAmount = required(idx, "売上金額");
            int max = Math.max(Math.max(Math.max(iDate, iClass), Math.max(iCustomer, iProduct)), Math.max(Math.max(iPart, iQty), iAmount));
            String line;
            while ((line = br.readLine()) != null) {
                if (line.isEmpty()) continue;
                List<String> row = parseCsvLine(line);
                if (row.size() <= max) continue;
                String cid = norm(row.get(iCustomer));
                if (!targetIds.contains(cid)) continue;
                int[] ym = parseYearMonth(row.get(iDate));
                if (ym[0] != goal.year || ym[1] < 4 || ym[1] > 9) continue;
                String rawClass = safe(row.get(iClass));
                String cat;
                if ("段ボール".equals(rawClass) || "全外注品".equals(rawClass)) cat = CAT_CARD;
                else if ("商品".equals(rawClass)) cat = CAT_GOODS;
                else if ("版代型代".equals(rawClass)) cat = CAT_PLATE;
                else continue;
                int mi = ym[1] - 4;
                Metrics metrics = out.actuals.get(cid).byCat.get(cat);
                metrics.amount[mi] += parseDouble(row.get(iAmount));
                if (CAT_CARD.equals(cat)) {
                    String k = key(cid, norm(row.get(iProduct)), norm(row.get(iPart)));
                    Double sqm = sqmLookup.get(k);
                    if (sqm != null) {
                        metrics.sqm[mi] += parseDouble(row.get(iQty)) * sqm;
                        out.joinHits++;
                    } else {
                        out.joinMisses++;
                    }
                }
            }
        }

        CatSet all = sumSets(out.actuals, false);
        LinkedHashMap<String, CatSet> reordered = new LinkedHashMap<>();
        reordered.put("ALL", all);
        reordered.putAll(out.actuals);
        out.actuals.clear();
        out.actuals.putAll(reordered);
        return out;
    }

    private static int[] parseYearMonth(String s) {
        try {
            String[] p = safe(s).split("/");
            return new int[]{Integer.parseInt(p[0]), Integer.parseInt(p[1])};
        } catch (Exception e) {
            return new int[]{0, 0};
        }
    }

    private static Map<String, Integer> headerIndex(List<String> header) {
        Map<String, Integer> map = new HashMap<>();
        for (int i = 0; i < header.size(); i++) map.put(stripBom(header.get(i)).trim(), i);
        return map;
    }

    private static int required(Map<String, Integer> idx, String... names) {
        for (String n : names) if (idx.containsKey(n)) return idx.get(n);
        throw new IllegalArgumentException("CSV列が見つかりません: " + String.join("/", names));
    }

    private static List<String> parseCsvLine(String line) {
        List<String> out = new ArrayList<>();
        StringBuilder sb = new StringBuilder();
        boolean quoted = false;
        for (int i = 0; i < line.length(); i++) {
            char ch = line.charAt(i);
            if (ch == '"') {
                if (quoted && i + 1 < line.length() && line.charAt(i + 1) == '"') {
                    sb.append('"'); i++;
                } else quoted = !quoted;
            } else if (ch == ',' && !quoted) {
                out.add(sb.toString()); sb.setLength(0);
            } else {
                sb.append(ch);
            }
        }
        out.add(sb.toString());
        return out;
    }

    private static String key(String a, String b, String c) { return a + "|" + b + "|" + c; }

    private static String norm(String s) {
        String v = safe(s).trim();
        if (v.endsWith(".0")) v = v.substring(0, v.length() - 2);
        return v;
    }

    private static String safe(String s) { return s == null ? "" : s; }

    private static String stripBom(String s) {
        if (s != null && !s.isEmpty() && s.charAt(0) == '\ufeff') return s.substring(1);
        return s == null ? "" : s;
    }

    private static double parseDouble(String s) {
        if (s == null) return 0.0;
        try {
            String v = s.trim().replace(",", "");
            if (v.isEmpty() || v.startsWith("=")) return 0.0;
            return Double.parseDouble(v);
        } catch (Exception e) {
            return 0.0;
        }
    }

    private static String displayName(Context context, Uri uri) {
        if (uri == null) return "";
        try {
            Cursor c = context.getContentResolver().query(uri, new String[]{OpenableColumns.DISPLAY_NAME}, null, null, null);
            if (c != null) {
                try {
                    if (c.moveToFirst()) return safe(c.getString(0));
                } finally { c.close(); }
            }
        } catch (Exception ignored) {}
        String last = uri.getLastPathSegment();
        return last == null ? "" : last;
    }
}
from pathlib import Path

main = Path("recipe-book/app/src/main/java/dev/ryu4696/recipebook/MainActivity.java")
s = main.read_text(encoding="utf-8")

old = '''            Button tab = idx == viewingSectionIndex
                    ? selectedButton(section.name)
                    : button(section.name, v -> {
                        rememberCurrentStepPage();
                        int samePage = viewPage;
                        viewingSectionIndex = idx;
                        if (samePage > 0) {
                            viewPage = Math.min(samePage, Math.max(1, r.sections.get(idx).steps.size()));
                            lastStepPageBySection.put(idx, viewPage);
                        } else {
                            viewPage = 0;
                        }
                        showRecipeView();
                    });
'''
new = '''            Button tab = idx == viewingSectionIndex
                    ? selectedButton(section.name)
                    : button(section.name, v -> {
                        rememberCurrentStepPage();
                        boolean wasInSteps = viewPage > 0;
                        viewingSectionIndex = idx;
                        viewPage = wasInSteps
                                ? lastStepForSection(idx, r.sections.get(idx).steps.size())
                                : 0;
                        showRecipeView();
                    });
'''
if old not in s:
    raise SystemExit("section switching block not found")
s = s.replace(old, new)
main.write_text(s, encoding="utf-8")

gradle = Path("recipe-book/app/build.gradle")
g = gradle.read_text(encoding="utf-8")
if "versionCode 5\n        versionName '1.1.1'" not in g:
    raise SystemExit("v1.1.1 version marker not found")
g = g.replace("versionCode 5\n        versionName '1.1.1'", "versionCode 6\n        versionName '1.1.2'")
gradle.write_text(g, encoding="utf-8")

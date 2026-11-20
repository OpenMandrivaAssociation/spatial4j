Name:		spatial4j
Version:	0.8
Release:	1
Summary:	Geospatial shapes and distance calculations for Java
Group:		Development/Java
License:	ASL 2.0
URL:		https://github.com/locationtech/spatial4j
Source0:	https://github.com/locationtech/spatial4j/archive/refs/tags/spatial4j-%{version}.tar.gz#/spatial4j-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	python
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	mvn(org.noggit:noggit)

%description
Spatial4j provides geospatial shapes, distance calculations, and
readers and writers for those shapes. 0.8 lives under
org.locationtech.spatial4j (was com.spatial4j). This build uses the
system noggit jar for GeoJSON. Optional JTS and Jackson modules are
left out because JTS is not published.

%prep
%autosetup -n spatial4j-spatial4j-%{version}
rm -rf src/test
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete
python - <<'PY'
import pathlib
import re

src = pathlib.Path("src/main/java")
for rel in (
    "org/locationtech/spatial4j/context/jts",
    "org/locationtech/spatial4j/io/jts",
    "org/locationtech/spatial4j/shape/jts",
    "org/locationtech/spatial4j/io/jackson",
):
    path = src / rel
    if path.is_dir():
        import shutil
        shutil.rmtree(path)
    else:
        raise SystemExit("missing " + rel)

# Unused JTS import left in the non-JTS PolyshapeReader.
poly = src / "org/locationtech/spatial4j/io/PolyshapeReader.java"
text = poly.read_text(encoding="utf-8")
text2 = re.sub(r"^import org\.locationtech\.jts\.geom\.LinearRing;\n", "", text, count=1, flags=re.M)
if text2 == text:
    raise SystemExit("LinearRing import not found")
poly.write_text(text2, encoding="utf-8")

java_files = sorted(src.rglob("*.java"))
if len(java_files) != 50:
    raise SystemExit("java files " + str(len(java_files)))
if list(pathlib.Path(".").rglob("*.jar")):
    raise SystemExit("prebuilt jar remains")
for path in java_files:
    t = path.read_text(encoding="utf-8")
    if "locationtech.jts" in t or "vividsolutions" in t or "fasterxml" in t:
        raise SystemExit("forbidden import in " + str(path))
PY

%build
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"

CP="%{_javadir}/noggit.jar"
test -s "$CP"
mkdir -p out
find src/main/java -name '*.java' > out.list
test "$(wc -l < out.list)" -eq 50
javac --release 8 -encoding UTF-8 -Xlint:-options -proc:none \
	-cp "$CP" -d out @out.list
javap -verbose -cp out org.locationtech.spatial4j.context.SpatialContext \
	| grep -F -q 'major version: 52'

jar cf spatial4j.jar -C out .
jar i spatial4j.jar
jar tf spatial4j.jar | grep -E '\.(java|jar|so|node|wasm)$' && exit 1 || true

cat > spatial4j.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.locationtech.spatial4j</groupId>
  <artifactId>spatial4j</artifactId>
  <version>0.8</version>
  <packaging>jar</packaging>
  <name>Spatial4j</name>
  <description>Geospatial shapes. GeoJSON uses the system noggit jar.</description>
  <url>https://github.com/locationtech/spatial4j</url>
  <licenses>
    <license>
      <name>Apache License, Version 2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.noggit</groupId>
      <artifactId>noggit</artifactId>
      <version>0.8</version>
    </dependency>
  </dependencies>
</project>
EOF

%install
set -eo pipefail
sysjar install --buildroot %{buildroot} \
	--artifact spatial4j.pom:spatial4j.jar \
	--file-name spatial4j \
	--filelist .mfiles

%check
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
JAR=%{buildroot}%{_javadir}/spatial4j.jar
test -s "$JAR"
mkdir -p check
cat > check/Check.java << 'EOF'
import org.locationtech.spatial4j.context.SpatialContext;
import org.locationtech.spatial4j.shape.Point;
import org.locationtech.spatial4j.shape.Shape;
public class Check {
	public static void main(String[] args) throws Exception {
		SpatialContext ctx = SpatialContext.GEO;
		Point p = ctx.makePoint(-122.4194, 37.7749);
		Shape box = ctx.makeRectangle(-123, -122, 37, 38);
		Shape wkt = ctx.readShapeFromWkt("POINT(-122.4194 37.7749)");
		if (!box.relate(p).intersects()) {
			throw new IllegalStateException("point outside box");
		}
		System.out.println("spatial4j_ok " + p.getX() + " " + box.getArea(ctx));
	}
}
EOF
javac --release 8 -encoding UTF-8 -Xlint:-options -proc:none \
	-cp "$JAR" -d check check/Check.java
java -cp "check:$JAR" Check > check/out.txt
cat check/out.txt
grep -F -q 'spatial4j_ok -122.4194' check/out.txt

%files -f .mfiles
%license asl-v20.txt
%doc README.md CHANGES.md

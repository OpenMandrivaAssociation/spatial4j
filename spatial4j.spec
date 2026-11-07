Name:		spatial4j
Version:	0.5
Release:	1
Summary:	Geospatial shapes and distance calculations for Java
Group:		Development/Java
License:	ASL 2.0
URL:		https://github.com/locationtech/spatial4j
Source0:	https://github.com/locationtech/spatial4j/archive/refs/tags/spatial4j-%{version}.tar.gz#/spatial4j-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildRequires:	mvn(org.noggit:noggit)
BuildSystem:	maven
BuildOption(install):	--file-name spatial4j

Obsoletes:	%{name}-javadoc < %{version}-%{release}

%description
Spatial4j provides geospatial shapes, distance calculations, and
readers and writers for those shapes. 0.5 adds WKT writing, GeoJSON,
and the Polyshape format, and it requires Java 7 upstream. This build
uses the system noggit jar for GeoJSON and raises the compiler source
level to 1.8. JTS shapes are left out because JTS is not published.
Tests are skipped.

%prep
%autosetup -n spatial4j-spatial4j-%{version}
rm -rf src/test
python - <<'PY'
import shutil
from pathlib import Path

src = Path("src/main/java")
for rel in (
    "com/spatial4j/core/context/jts",
    "com/spatial4j/core/io/jts",
    "com/spatial4j/core/shape/jts",
):
    path = src / rel
    if path.is_dir():
        shutil.rmtree(path)
    else:
        raise SystemExit("missing " + rel)
java_files = list(src.rglob("*.java"))
if len(java_files) != 47:
    raise SystemExit("java files " + str(len(java_files)))
if list(Path(".").rglob("*.jar")):
    raise SystemExit("prebuilt jar remains")
for path in java_files:
    text = path.read_text(encoding="utf-8")
    if "com.vividsolutions" in text:
        raise SystemExit("jts import remains in " + str(path))

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.spatial4j</groupId>
  <artifactId>spatial4j</artifactId>
  <version>%{version}</version>
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
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.source>1.8</maven.compiler.source>
    <maven.compiler.target>1.8</maven.compiler.target>
  </properties>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <source>1.8</source>
          <target>1.8</target>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
for needle in (
    "<artifactId>spatial4j</artifactId>",
    "<artifactId>noggit</artifactId>",
    "<version>0.8</version>",
    "<version>%{version}</version>",
    "<source>1.8</source>",
    "<target>1.8</target>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in ("junit", "oss-parent", "vividsolutions", "<source>1.7</source>", "SNAPSHOT", "<release>", "slf4j"):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
PY

%build -a
java --module-path target/spatial4j-%{version}.jar --describe-module spatial4j > module-describe.txt
# A versioned jar prints "name@version ... automatic", not "name automatic".
grep -q '^spatial4j' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }

%files -f .mfiles
%doc LICENSE.txt README.md CHANGES.md

sc_path = d:\games\sc
launcher = d:\games\sc\Chaoslauncher\chaoslauncher.exe
src = src

all: mpq

run: patch
	@$(launcher)

patch: mpq
	@echo Overwriting existing patch_rt.mpq
	@cp build/patch_rt.mpq $(sc_path)\patch_rt.mpq

mpq: combined_scripts
	@echo Creating MPQ
	@python tools\pyai.pyw -c -w -m ../build/patch_rt.mpq ../build/combined.pyai ../build/aiscript.bin ../build/bwscript.bin

bins: combined_scripts
	@echo Creating script binaries
	@python tools\pyai.pyw -c -w ../build/combined.pyai ../build/aiscript.bin ../build/bwscript.bin

combined_scripts: terran.pyai zerg.pyai protoss.pyai
	@echo Combining scripts
	@cat build/terran.pyai build/zerg.pyai build/protoss.pyai > build/combined.pyai

%.pyai:
	@echo Building $@
	@node tools/build_ai $(subst .pyai,,$@) build/$@;


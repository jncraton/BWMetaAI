sc_path = .
launcher = chaoslauncher.exe
src = src
config = default

all: mpq

run: patch
	@$(launcher)

patch: mpq
	@echo Overwriting existing patch_rt.mpq
	@cp $(sc_path)/patch_rt_bwmetaai.mpq $(sc_path)\patch_rt.mpq

mpq: combined_scripts $(sc_path)/patch_rt_original.mpq
	@echo Creating MPQ
	@cp $(sc_path)/patch_rt_original.mpq build/patch_rt.mpq
	@python tools/PyAI.pyw -c -w -m ../build/patch_rt.mpq ../build/combined.pyai ../build/aiscript.bin ../build/bwscript.bin
	@cp build/patch_rt.mpq $(sc_path)/patch_rt_bwmetaai.mpq

bins: combined_scripts
	@echo Creating script binaries
	@python tools\pyai.pyw -c -w ../build/combined.pyai ../build/aiscript.bin ../build/bwscript.bin

combined_scripts: terran.pyai zerg.pyai protoss.pyai
	@echo Combining scripts
	@cat build/terran.pyai build/zerg.pyai build/protoss.pyai > build/combined.pyai

%.pyai:
	@echo Building $@
	@cp tools/config_$(config).json tools/config.json
	@node tools/build_ai $(subst .pyai,,$@) build/$@;
	@rm tools/config.json

$(sc_path)/patch_rt_original.mpq:
	@cp $(sc_path)/patch_rt.mpq $(sc_path)/patch_rt_original.mpq

clean:
	@rm -f build/*.mpq
	@rm -f build/*.pyai
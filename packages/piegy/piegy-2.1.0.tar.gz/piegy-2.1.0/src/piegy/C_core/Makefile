# Compiler and flags
CC = gcc

#### Common Flags ####

## Flags for Max Speed ##
# standard
CFLAGS_COMMON = -O3 -flto -std=c99 -DNDEBUG -ffp-contract=fast
LDFLAGS_COMMON = -flto

## Flags for Debugging ##
# slower, debuggable with lldb, with Address Sanitizer. Don't use in python
#CFLAGS = -g -std=c99 -Wall -Wextra -fsanitize=address,undefined -fno-omit-frame-pointer
#LDFLAGS = -fsanitize=address,undefined
# slower, regular build, allow lldb
#CFLAGS = -g -std=c99 -Wall -Wextra
#LDFLAGS = 

# Enable auto header dependency tracking
DEPFLAGS = -MMD -MP
CFLAGS += $(DEPFLAGS)


#### OS specific ####
UNAME_S := $(shell uname -s)

ifeq ($(UNAME_S),Darwin)
    # macOS-specific flags
    CFLAGS = $(CFLAGS_COMMON) -fPIC -mmacosx-version-min=11.0 -arch arm64 $(DEPFLAGS)
    LDFLAGS = $(LDFLAGS_COMMON)
else ifeq ($(UNAME_S),Linux)
    # Linux-specific flags
    CFLAGS = $(CFLAGS_COMMON) -fPIC $(DEPFLAGS)
    LDFLAGS = $(LDFLAGS_COMMON)
else ifeq ($(UNAME_S),Windows_NT)
    # Windows-specific flags
    CFLAGS = $(CFLAGS_COMMON) -D_WIN32_WINNT=0x0A00 -DWINVER=0x0A00 $(DEPFLAGS)
    LDFLAGS = $(LDFLAGS_COMMON)
else
    # Default fallback
    CFLAGS = $(CFLAGS_COMMON) -fPIC $(DEPFLAGS)
    LDFLAGS = $(LDFLAGS_COMMON)
endif



#### Targets and Commands ####

# Source and object files
SRC = sim_funcs.c model.c patch.c 
RUNNER_SRC = runner.c
OBJ = $(SRC:.c=.o)
RUNNER_OBJ = $(RUNNER_SRC:.c=.o)
RUNNER_DEPS = $(RUNNER_OBJ:.o=.d)
DEPS = $(OBJ:.o=.d) $(RUNNER_DEPS)

# Executable name
TEST = runner
ifeq ($(OS),Windows_NT)
    SHARED_LIB = piegyc.dll
else
    SHARED_LIB = piegyc.so
endif


# Default target
all: $(SHARED_LIB) $(TEST)

# test file
test: $(TEST)

# shared library
so: $(SHARED_LIB)

# Link the final binary
$(TEST): $(OBJ) $(RUNNER_OBJ)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

# Shared library target
$(SHARED_LIB): $(OBJ)
	$(CC) $(CFLAGS) $(LDFLAGS) -shared -o $@ $^

# Compile source files to object files
%.o: %.c
	$(CC) $(CFLAGS) $(LDFLAGS) -c $< -o $@

# Clean build files
clean:
	rm -f $(OBJ) $(RUNNER_OBJ) $(TEST) $(SHARED_LIB) $(DEPS)

# Rebuild target: clean then all
re: clean all

# Include auto-generated dependency files
-include $(DEPS)

.PHONY: all clean re test so




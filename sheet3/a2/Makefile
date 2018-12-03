CC=gcc

OBJ_DIR=build
TEST_DIR=test_suite
MKDIR_P = mkdir -p

SAND_OBJ=sandbox.so
TEST_OBJ=test

all: sandbox.c $(TEST_DIR)/test.c
	${MKDIR_P} ${OBJ_DIR}
	$(CC) -fPIC -shared -o $(OBJ_DIR)/$(SAND_OBJ) sandbox.c -ldl
	$(CC) -o $(OBJ_DIR)/$(TEST_OBJ) $(TEST_DIR)/test.c

clean:
	rm -rf $(OBJ_DIR)
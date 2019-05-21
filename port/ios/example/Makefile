TARGET := iphone:clang
TARGET_IPHONEOS_DEPLOYMENT_VERSION = 3.0
ARCHS = armv7 arm64

BTSTACK_ROOT=../../..
# VPATH += $(BTSTACK_ROOT)/platform/daemon/example

ADDITIONAL_CFLAGS  = -I.. \
	-I$(BTSTACK_ROOT)/src \
	-I$(BTSTACK_ROOT)/platform/daemon/src \
	-I$(BTSTACK_ROOT)/platform/posix  \
	-I$(BTSTACK_ROOT)/platform/corefoundation  \
	-Wno-implicit-function-declaration

ifeq ($(FINALPACKAGE),1)
ADDITIONAL_LDFLAGS = -L../.theos/obj -lBTstack
else 
ADDITIONAL_LDFLAGS = -L../.theos/obj/debug -lBTstack
endif

TOOL_NAME = inquiry l2cap_test rfcomm_echo rfcomm_cat rfcomm_test l2cap_server l2cap_throughput

inquiry_FILES          = $(BTSTACK_ROOT)/platform/daemon/example/inquiry.c
rfcomm_echo_FILES      = $(BTSTACK_ROOT)/platform/daemon/example/rfcomm_echo.c
rfcomm_cat_FILES       = $(BTSTACK_ROOT)/platform/daemon/example/rfcomm_cat.c
rfcomm_test_FILES      = $(BTSTACK_ROOT)/platform/daemon/example/rfcomm_test.c
l2cap_test_FILES       = $(BTSTACK_ROOT)/platform/daemon/example/test.c
l2cap_server_FILES     = $(BTSTACK_ROOT)/platform/daemon/example/l2cap_server.c
l2cap_throughput_FILES = $(BTSTACK_ROOT)/platform/daemon/example/l2cap_throughput.c

inquiry_CODESIGN_FLAGS = -S../ent.xml
rfcomm_echo_CODESIGN_FLAGS = -S../ent.xml
rfcomm_cat_CODESIGN_FLAGS = -S../ent.xml
rfcomm_test_CODESIGN_FLAGS = -S../ent.xml
l2cap_test_CODESIGN_FLAGS = -S../ent.xml
l2cap_server_CODESIGN_FLAGS = -S../ent.xml
l2cap_throughput_CODESIGN_FLAGS = -S../ent.xml

include $(THEOS)/makefiles/common.mk
include $(THEOS_MAKE_PATH)/tool.mk

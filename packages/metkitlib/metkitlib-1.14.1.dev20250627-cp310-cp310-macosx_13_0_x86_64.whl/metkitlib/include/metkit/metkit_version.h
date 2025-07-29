#ifndef metkit_version_h
#define metkit_version_h

#define metkit_VERSION_STR "1.14.1.dev20250627"
#define metkit_VERSION     "1.14.1"

#define metkit_VERSION_MAJOR 1
#define metkit_VERSION_MINOR 14
#define metkit_VERSION_PATCH 1

#define metkit_GIT_SHA1 "25e0ea40d523f4f188917dc70b3d0705186e9e76"

#ifdef __cplusplus
extern "C" {
#endif

const char * metkit_version();

unsigned int metkit_version_int();

const char * metkit_version_str();

const char * metkit_git_sha1();

#ifdef __cplusplus
}
#endif


#endif // metkit_version_h

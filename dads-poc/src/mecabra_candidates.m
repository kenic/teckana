// Experimental private ABI, observed on macOS 27.2 (26B123), arm64.
// No accept, save, adapt, reset, or dictionary mutation functions are resolved.
#import <Foundation/Foundation.h>
#include <dlfcn.h>
#include <sandbox.h>
#include <unistd.h>

typedef void *Engine;
typedef void *Candidate;
static void *symbol(void *h,const char *name) {
    void *p=dlsym(h,name);
    if(!p){fprintf(stderr,"Missing symbol: %s\n",name);exit(2);} return p;
}
int main(int argc,char **argv) {
    if(argc!=3){fprintf(stderr,"usage: mecabra_candidates HIRAGANA RAW_LIMIT\n");return 64;}
    char *end; long limit=strtol(argv[2],&end,10);
    if(*end || limit<1 || limit>100000)return 64;
    alarm(30);
    // External mode is ONLY for a host already enforcing filesystem restrictions.
    // A normal Terminal invocation must leave this variable unset.
    BOOL external=getenv("MECABRA_ALREADY_SANDBOXED") &&
        strcmp(getenv("MECABRA_ALREADY_SANDBOXED"),"1")==0;
    if(!external){
        char *error=NULL;
        if(sandbox_init("(version 1)(allow default)(deny file-write*)(deny network*)",0,&error)){
            fprintf(stderr,"Cannot enforce read-only profile: %s\n",error?error:"unknown");
            if(error)sandbox_free_error(error);return 77;
        }
    }
    @autoreleasepool {
        NSString *input=[NSString stringWithUTF8String:argv[1]];
        if(!input.length || input.length>256)return 64;
        void *h=dlopen("/usr/lib/libmecabra.dylib",RTLD_NOW|RTLD_LOCAL);
        if(!h){fprintf(stderr,"dlopen: %s\n",dlerror());return 2;}
        Engine (*create)(CFDictionaryRef)=symbol(h,"MecabraCreate");
        int (*analyze)(Engine,CFStringRef,uint64_t)=symbol(h,"MecabraAnalyzeString");
        Candidate (*next)(Engine)=symbol(h,"MecabraGetNextCandidate");
        CFStringRef (*surface)(Candidate)=symbol(h,"MecabraCandidateGetSurface");
        CFStringRef (*reading)(Candidate)=symbol(h,"MecabraCandidateGetAnalysisString");
        CFStringRef (*dictionaryReading)(Candidate)=symbol(h,"MecabraCandidateGetDictionaryReading");
        void (*release)(Engine)=symbol(h,"MecabraRelease");
        NSMutableDictionary *options=[NSMutableDictionary dictionary];
        const char *disabled[]={"kMecabraCreationLearningEnabledKey",
            "kMecabraCreationSyncLearningDataKey","kMecabraCreationDynamicLanguageModelEnabledKey"};
        for(int i=0;i<3;i++)options[(__bridge NSString*)*(CFStringRef*)symbol(h,disabled[i])]=@NO;
        options[(__bridge NSString*)*(CFStringRef*)symbol(h,"kMecabraCreationInputMethodTypeKey")]=@1;
        Engine engine=create((__bridge CFDictionaryRef)options);
        if(!engine){fprintf(stderr,"Engine creation failed\n");return 3;}
        // 2 is an experimentally verified conversion-like mode, not an Apple SDK constant.
        int ok=analyze(engine,(__bridge CFStringRef)input,2);
        if(!ok){release(engine);fprintf(stderr,"Analysis failed\n");return 4;}
        NSMutableArray *rows=[NSMutableArray array];
        BOOL exhausted=NO;
        for(long i=0;i<limit;i++) {
            Candidate candidate=next(engine);
            if(!candidate){exhausted=YES;break;}
            NSString *text=(__bridge NSString*)surface(candidate);
            NSString *read=(__bridge NSString*)reading(candidate);
            NSString *dict=(__bridge NSString*)dictionaryReading(candidate);
            if(!text || !read){release(engine);fprintf(stderr,"Invalid candidate\n");return 5;}
            // Copy values before advancing the engine; Get ownership is undocumented.
            [rows addObject:@{@"raw_rank":@(i+1),@"surface":[text copy],
                @"analysis_reading":[read copy],@"dictionary_reading":dict?[dict copy]:@""}];
        }
        if(!exhausted)exhausted=(next(engine)==NULL); // Distinguish exact boundary from truncation.
        release(engine);
        NSDictionary *result=@{@"reading":input,@"analysis_flags":@2,@"input_method_type":@1,
            @"options":options,@"enumeration_exhausted":@(exhausted),@"raw_limit":@(limit),
            @"guard":external?@"external-host-restrictions":@"deny-file-write-and-network",
            @"os":NSProcessInfo.processInfo.operatingSystemVersionString,@"candidates":rows};
        NSError *error=nil;NSData *json=[NSJSONSerialization dataWithJSONObject:result options:0 error:&error];
        if(!json){fprintf(stderr,"JSON failed\n");return 6;}
        fwrite(json.bytes,1,json.length,stdout);putchar('\n');
    }
    return 0;
}

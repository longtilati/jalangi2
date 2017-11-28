(function(sandbox) {
    function MyAnalysis() {
        this.scriptEnter = function(iid, instrumentedFileName, originalFileName) {
            console.log("enter script: " + originalFileName);
        };
        this.invokeFunPre = function(iid, f, base, args, isConstructor, isMethod, functionIid, functionSid) {
            // var location = sandbox.iidToLocation(sandbox.sid, iid);
            console.log("before invoking function: " + f.name);
        };
        this.invokeFun = function(iid, f, base, args, result, isConstructor, isMethod, functionIid, functionSid) {
            console.log("after invoking function: " + f.name);
        };
        this.functionEnter = function(iid, f, dis, args) {
            console.log("enter function: " + f.name);
            console.log("arguments: " + args);
        };
        this.functionExit = function(iid, returnVal, wrappedExceptionVal) {
            console.log("exit function with value " + returnVal);
        };
    }
    sandbox.analysis = new MyAnalysis();
})(J$);
(function(sandbox) {
    function MyAnalysis() {
        var filename;
        var functionStack = [];
        this.scriptEnter = function(iid, instrumentedFileName, originalFileName) {
            filename = originalFileName;
            console.log("enter script: " + originalFileName);
        };
        this.invokeFunPre = function(iid, f, base, args, isConstructor, isMethod, functionIid, functionSid) {
            // var location = sandbox.iidToLocation(sandbox.sid, iid);
            console.log("before invoking function: " + (f.name ? f.name : "anonymous"));
        };
        this.invokeFun = function(iid, f, base, args, result, isConstructor, isMethod, functionIid, functionSid) {
            console.log("after invoking function: " + (f.name ? f.name : "anonymous"));
        };
        this.functionEnter = function(iid, f, dis, args) {
            functionStack.push(f.name ? f.name : "anonymous");
            var a = [];
            for (var i = 0; i < args.length; i++) {
                a[i] = args[i];
            }
            console.log("enter function [" + (f.name ? f.name : "anonymous") + "] with arguments [" + a.join() + "]");
        };
        this.functionExit = function(iid, returnVal, wrappedExceptionVal) {
            console.log("exit function [" + functionStack.pop() + "] with return value [" + returnVal + "]");
        };
        this.scriptExit = function(iid, wrappedExceptionVal) {
            console.log("exit script: " + filename);
        };
    }
    sandbox.analysis = new MyAnalysis();
})(J$);
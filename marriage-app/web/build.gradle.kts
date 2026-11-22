plugins {
    alias(libs.plugins.kotlin.multiplatform)
}

kotlin {
    js {
        browser()
        binaries.executable()
    }
    sourceSets {
        // The web version shares the engine's rules, bots and text.
        jsMain {
            kotlin.srcDir("../engine/src/main/kotlin")
        }
    }
}

/** Copies the compiled script and the page into build/site, ready to publish. */
val site by tasks.registering(Copy::class) {
    dependsOn("compileProductionExecutableKotlinJs")
    from(layout.buildDirectory.dir("compileSync/js/main/productionExecutable/kotlin")) {
        include("*.js")
        rename { "marriage.js" }
    }
    from("src/jsMain/resources")
    into(layout.buildDirectory.dir("site"))
}

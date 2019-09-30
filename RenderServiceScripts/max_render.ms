resetMaxFile #noPrompt
SetQuietMode true
logsystem.logName "Output\\render_log.txt"
units.SystemType = #Meters

function initializeRPR = (

    renderers.current = Radeon_ProRender()
    renderers.current.timeLimit = 1
    black_jpg = "{res_path}\\initializeRPR.jpg"
    render outputfile:black_jpg

)

function rpr_render = (
	
	assetsFile = "{scene_path}"
	loadMaxFile assetsFile useFileUnits:true quiet:true
	
    rpr = Radeon_ProRender()
    if classof renderers.current != classof rpr do (
        renderers.current = Radeon_ProRender()
    )

    if {min_samples} > 0 then (
       renderers.current.samplesMin = {min_samples} 
    )
    if {max_samples} > 0 then (
       renderers.current.samplesMax = {max_samples} 
    )
    if {noise_threshold} > 0 then (
       renderers.current.adaptiveNoiseThreshold = {noise_threshold} 
    ) 

    if {width} > 0 then (
        renderWidth = {width}
    )
    if {height} > 0 then (
        renderHeight = {height}
    )

    image_path = "{res_path}\\Output\\" + maxFileName + ".jpg"

    rstart = timeStamp()
    render outputfile:image_path
    rend = timeStamp()
    relapsed = ((rend - rstart) / 1000.0)

    json_path = "{res_path}\\render_info.json"
    a = (createFile json_path mode:"w")

    json_line = "{{\n" 
    format "%" json_line to:a

    json_line = "  \"min_samples\": " + (renderers.current.samplesMin as string) + ",\n"
    format "%" json_line to:a

    json_line = "  \"max_samples\": " + (renderers.current.samplesMax as string) + ",\n"
    format "%" json_line to:a

    json_line = "  \"noise_threshold\": " + (renderers.current.adaptiveNoiseThreshold as string) + ",\n"
    format "%" json_line to:a

    json_line = "  \"render_time\": " + (relapsed as string) + ",\n"
    format "%" json_line to:a 

    json_line = "  \"width\": " + (renderWidth as string) + ",\n"
    format "%" json_line to:a 

    json_line = "  \"height\": " + (renderHeight as string) + "\n"
    format "%" json_line to:a 

    json_line = "}}\n"
    format "%" json_line to:a 

    flush a
    close a 

)

initializeRPR()
rpr_render()
resetMaxFile #noPrompt
quitMax #noPrompt

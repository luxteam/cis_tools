resetMaxFile #noPrompt
SetQuietMode true
logsystem.logName "Output\\rprLog.txt"
units.SystemType = #Meters

function initializeRPR = (

    renderers.current = Radeon_ProRender()
    renderers.current.passLimit = 1
    renderers.current.renderDevice = {render_device_type}
    renderers.current.renderLimit = 1
    black_jpg = "{res_path}\\initializeRPR.jpg"
    render outputfile:black_jpg

)

function rpr_render = (
	
	assetsFile = "{res_path}\\{scene}"
	loadMaxFile assetsFile useFileUnits:true quiet:true
	
    pass_limit = {pass_limit}
    if (pass_limit > 0) then {{
        renderers.current.passLimit = {pass_limit}
    }} else if (pass_limit > 1000) then {{
        renderers.current.passLimit = 1000
    }}
	
    renderers.current.renderDevice = {render_device_type}
    renderers.current.renderLimit = 1

    image_path = "{res_path}\\Output\\{scene_name}.jpg"

    rstart = timeStamp()
    render outputfile:image_path
    rend = timeStamp()
    relapsed = ((rend - rstart) / 1000.0)

    json_path = "{res_path}\\render_info.json"
    a = (createFile json_path mode:"w")

    json_line = "{{\n" 
    format "%" json_line to:a

    json_line = "  \"pass_limit\": " + (renderers.current.passLimit as string) + ",\n"
    format "%" json_line to:a

    json_line = "  \"render_time\": " + (relapsed as string) + ",\n"
    format "%" json_line to:a 

    json_line = "  \"resolution_x\": " + (renderWidth as string) + ",\n"
    format "%" json_line to:a 

    json_line = "  \"resolution_x\": " + (renderHeight as string) + ",\n"
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

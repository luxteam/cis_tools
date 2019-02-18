resetMaxFile #noPrompt
SetQuietMode true
logsystem.logName "Output\\max_log.txt"
units.SystemType = #Meters

function rpr_render = (
	
	assetsFile = "{res_path}\\{scene}"
	loadMaxFile assetsFile useFileUnits:true quiet:true
	
	renderers.current = Radeon_ProRender()
    renderers.current.passLimit = {pass_limit}
	
    renderers.current.renderDevice = {render_device_type}
    renderers.current.renderLimit = 1
	
    image_path = "{res_path}\\Output\\"
    filename = "{scene_name}.jpg"
    image_path = image_path + filename

    rstart = timeStamp()
    render outputfile:image_path
    rend = timeStamp()
    relapsed = ((rend - rstart) / 1000.0)

    ver_max = filterString (getdir #maxroot) "\\"

    json_path = "{res_path}\\Output\\{scene_name}.json"
    a = (createFile json_path mode:"w")
    format "%" "[\n" to:a

    json_line = " {{\n" 
    format "%" json_line to:a

    json_line = "  \"tool\": \"" + ver_max[ver_max.count] +  "\",\n"
    format "%" json_line to:a

    json_line = "  \"render_device_type\": \"" + "{render_device_type}" + "\",\n"
    format "%" json_line to:a

    json_line = "  \"pass_limit\": " + (renderers.current.passLimit as string) + ",\n"
    format "%" json_line to:a

    json_line = "  \"scene_name\": \"" + "{scene_name}" + "\",\n"
    format "%" json_line to:a

    json_line = "  \"date_time\": \"" + (localtime as String) + "\",\n"
    format "%" json_line to:a

    json_line = "  \"file_name\": \"" + filename + "\",\n"
    format "%" json_line to:a  

    json_line = "  \"render_time\": " + (relapsed as string) + ",\n"
    format "%" json_line to:a 

    json_line = "  \"plugin_version\": " + "no api" + ",\n"
    format "%" json_line to:a 

    json_line = "  \"core_version\": " + "no api" + ",\n"
    format "%" json_line to:a 

    json_line = "  \"resolution_x\": " + (renderWidth as string) + ",\n"
    format "%" json_line to:a 

    json_line = "  \"resolution_x\": " + (renderHeight as string) + ",\n"
    format "%" json_line to:a 

    json_line = " }}\n"
    format "%" json_line to:a 

    json_line = "]"
    format "%" json_line to:a
    flush a
    close a 

)

rpr_render()
resetMaxFile #noPrompt
quitMax #noPrompt
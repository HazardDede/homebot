{
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ":hass: |   *ENTITY STATES*  | :hass: "
			}
		},
        {
            "type": "divider"
        }
        %if not payload:
        ,{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "No Entities"
            }
        }
        %else:
        %for entity in payload:
		,{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*${entity.entity_id}* (_${entity.friendly_name}_): _${entity.state} ${entity.unit_of_measurement}_"
			}
		}
        %endfor
        %endif
	]
}
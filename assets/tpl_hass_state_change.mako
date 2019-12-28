{
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ":hass: |   *STATE CHANGES*  | :hass: "
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
                "text": "No state transitions"
            }
        }
        %else:
        %for entity in payload:
		,{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*${entity.entity_id}* (_${entity.friendly_name}_) switched to _${entity.state}_"
			}
		}
        %endfor
        %endif
	]
}